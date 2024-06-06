# Workflow as a Service (WaaS)

WaaS provides GitHub CI/CD workflows for building, testing, and deploying
application services.

WaaS is **not intended** to support build pipelines for libraries or IaC pipelines.

The workflows and deployment configuration files are provided via pull request
after subscribing your repository to WaaS. Changes to the WaaS config file will
result in a new pull request with the requested changes.

Checkout this [example WaaS pull
request](https://github.com/metro-digital-inner-source/waas-pull-request-example/pull/13)
to see what WaaS provides.

<details>
  <summary> List of features</summary>

### GitOps approach

All the Kubernetes templates, application configuration and workflows required
to configure and deploy the application service are stored in the subscribed
repository.

### Configure the CI/CD setup via subscription

By updating the WaaS subscription file a pull request is provided with the
requested changes.

### Configure application service environment variables securely

The application service's environment variables are easily configurable in both
encrypted files via [SOPS](https://github.com/getsops/sops) or
[Google Secret manager](https://cloud.google.com/secret-manager) for secrets
and in plain text files for non-secret values.

### Configure continuous deployment/delivery for any environment

For any of the configured environments in the subscription file it is possible
to specify which environment should be deployed automatically and which should
be deployed manually.

### Separation of releases and deployments

For any change to the subscribed repostory a GitHub release (draft or pre-) is created, which
can then be deployed to any environment at any time via the GitHub UI by making it a release.

### Automatic updates and bugfixes to WaaS

As improvements and bugfixes are done to WaaS, then those will be provided to
the subscribed repositories automatically via GitHub actions and via
pull-requests.

### Easy setup of local testing environment

The CI/CD GitHub workflows use [Skaffold](https://skaffold.dev/) to build and
push the container image, and [Skaffold](https://skaffold.dev/),
[Kustomize](https://kubernetes-sigs.github.io/kustomize) and
[SOPS](https://github.com/getsops/sops) to generate the Kubernetes templates
and deploy them to the target cluster. This workflow can be easily be
reproduced locally by installing the required tools and utilizing the generated
Skaffold and Kustomize configuration files in the subscribed repository.

</details>

<details><summary><b>Deploying WaaS for multiple GitHub organizations</b></summary>

## Configuring the GitHub App and deploying as GCF

1. Create a GitHub App which is available only for that specific organization: https://github.com/organizations/\<org-slug\>/settings/apps.

   The name of the GitHub app should be `waas-<organization_slug>`,
   because names of GitHubs apps have to be globally unique.

   Example: If you have an organization `metro-example` the GitHub app should be
   named `waas-metro-example`.

   That app must subscribe to `push` event in the target GitHub organization by providing the following permissions

   ```text
   Repository Permissions: (7 selected)

   Actions        : Read and Write
   Administration : Read-only
   Contents       : Read and Write
   Issues         : Read and Write
   Metadata       : Read-only
   Pull requests  : Read and Write
   Workflows      : Read and Write
   ```

1. Use the `Webhook URL` configured for the [WaaS-v2](https://github.com/organizations/metro-digital-inner-source/settings/apps/waas-v2) GitHub App as webhook URL for the newly created GitHub App.

1. The `Webhook secret` is stored as a secret in the Google secret manager of the `cf-2tier-github-prod-4b` GCP project with key `WEBHOOK_SECRET_WAAS`

1. Create following secrets in the Google Secret Manager under `cf-2tier-github-prod-4b` GCP project.

   For e.g, for a GitHub org with slug metro-example, following secrets must be created.

   ```text
   METRO_EXAMPLE_WAAS_APP_ID      #As value provide the APP ID of the GitHub app created in the above step.
   METRO_EXAMPLE_WAAS_PRIVATE_KEY #As value provide the base64 encoded PRIVATE KEY of the GitHub app created in the above step.
   ```

1. Reference the above created secrets in `deploy-dispatcher.yaml` and `deploy-worker.yaml` workflows which deploys the `waas-dispatcher` and `waas-worker-*` as a Google Cloud Functions.

## Configuring the rotation of Webhook Secret

1. The workflow `rotate-webhook-secret.yaml` is responsible for rotating the webhook secret weekly on a scheduled basis, every Wednesday

1. Whenever the GitHub App is configured for a new GitHub organization, the following changes must be done in order to rotate the webhook secret for the new GitHub organization

   1. Copy the secrets file `secrets/metro-digital-inner-source.secrets.yaml` and paste it under `secrets/` directory with the name of the new GitHub organization

      For e.g, for a GitHub org with slug `metro-example`, the name of the new secrets file must be `metro-example.secrets.yaml`

   1. Add the following secrets in the newly created secret file using `sops`

      ```yaml
      APP_ID: <App ID of the newly created GitHub App>
      PRIVATE_KEY: <Base64 encoded string of the private key generated fo the newly created GitHub App>
      ```

   1. Add the slug of the new GitHub org to the strategy matrix in `rotate-webhook-secret.yaml`

      ```yaml
      strategy:
        matrix:
          org:
            - metro-digital-inner-source
            - metro-digital-closed-source
            - metro-example
      ```

</details>

## How to get started with WaaS

### Subscribe to WaaS

Commit a WaaS config file `.github/waas.yaml` in your repository with this
example content to use `gke` as runtime provider:

```yaml
apiVersion: waas/v2
metadata:
  name: simple-app
profiles:
  - name: pp
    environment: test
    runtimeProvider:
      gcp:
        service: gke
  - name: prod
    environment: production
    runtimeProvider:
      gcp:
        service: gke
```

Do you want to import the waas/v2 schema into your VSCode IDE and validate the schema while creating a waas.yaml?

[Please click here to know how to import the JSON schema VSCode to validate your waas.yaml](https://github.com/metro-digital-inner-source/md-schema-store/tree/master#how-to-add-a-json-schema-to-vscode-to-validate-yaml-files)

If you are a new user of WaaS you should always use `apiVersion: waas/v2`
(or newer)!

Read more about the [available schemas](./documentation/apiVersion).

After pushing your commit you will get a pull-request in the repository, where
the necessary configuration steps are documented according to the WaaS
subscription.

[Full documentation of all the schema features](./documentation/apiVersion/waas-v2/v2.yaml)

[How to deploy a microservice to GKE with WaaS v2](./documentation/v2/how-to-deploy-a-microservice-to-gke-with-WaaS-v2.md)

[How to deploy a microservice to Cloud Run with WaaS v2](./documentation/v2/how-to-deploy-a-microservice-to-cloud-run-with-WaaS-v2.md)

## Extending the labels of K8s resources using WaaS

For adding additional labels to the K8s deployment use `LabelTransformer` in Kustomize.

[Documentation of kustomize LabelTransformer](https://kubectl.docs.kubernetes.io/references/kustomize/builtins/#_labeltransformer_)

### Using environment variable values for the labels

To add additional lables for K8s deployment by using environment varaibles provided in the WaaS workflows, provide them as comma separated labels in `.github/waas/pipeline.properties` as value for `WAAS_ADDITIONAL_SKAFFOLD_LABELS` using the environment variable name.

E.g.,

```yaml
# .github/waas/pipeline.properties.yaml

# WAAS_ENVIRONMENT, GIT_COMMIT_SHA and GIT_COMMIT_SHA_SHORT are provided as environment variables in the workflows provided by WAAS

WAAS_ADDITIONAL_SKAFFOLD_LABELS='environment=${WAAS_ENVIRONMENT},version=${GIT_COMMIT_SHA_SHORT}'
```

## How to configure WaaS for your use-case

We created example repositories, where you can check WaaS configurations
for different combinations of _runtimeProviders_ and _secretProviders_.

These examples are located in the GitHub
[product_demo team](https://github.com/orgs/metro-digital-inner-source/teams/product_demo/repositories).

After merging the pull-request from WaaS, you might want
to configure `skaffold.yaml` according to your use-case (e.g. regarding tests).

Here are some examples for how to configure it for [most common use-cases](./examples).

Checkout all available schemas [here](./documentation/apiVersion).

If you are a new user of WaaS you should use WaaS v2!

## Conceptual Background

WaaS v2 was build from scratch and leaves historical burden behind.

WaaS is designed to support CI/CD
([continuous integration](https://en.wikipedia.org/wiki/Continuous_integration),
[continuous delivery](https://en.wikipedia.org/wiki/Continuous_delivery),
[continuous deployment](https://en.wikipedia.org/wiki/Continuous_deployment))
and [trunk based development](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development) (recommended),
but can also be [used with](./documentation/v2/how-to-use-waas-with-git-flow.md)
[git flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) (not recommended).

We took inspiration from
the book [_Continous Delivery Pipelines_](https://leanpub.com/cd-pipelines)
by [Dave Farley](https://www.youtube.com/c/ContinuousDelivery).

![Book Continous Delivery Pipelines](./documentation/images/cd-book-dave-farley.jpg)

<details>
  <summary> More Background</summary>

### WaaS model of a deployment pipeline

The WaaS deployment pipeline is the first iteration of a full-blown one with
respect to Dave Farleys concept of it.

![WaaS deployment pipeline](./documentation/images/cd-pipeline-waas.png)

It is composed of three cycles:

- Commit Cycle
- Acceptance Cycle
- Deploy into Production

### Commit Cycle

The _Commit Cycle_ is triggered when a developer pushes to the default branch of
the GitHub repository.
The build (including build time test like e.g. Unit tests) is automatically
triggered and creates a so-called _Release-Candidate_ (on conceptual level).

The technical artifacts of the _Release-Candidate_ are:

- a docker image in the docker registry
- a GitHub draft release

### Acceptance Cycle

The _Acceptance Cycle_ consists of all tests running in all test environments
(configured in WaaS with `environment: test`).

During the _Acceptance Cycle_ the software (docker image) is installed in every
test environment in the order they appear in `waas.yaml`.
Then the tests are running. If they pass, the _Acceptance Cycle_ continues.

Technically the tests are configured in `skaffold.yaml` and are therefore part
of the skaffold deployment phase.

The result of a finished _Acceptance Cycle_ is so-called the _Releasable Outcome_ (on conceptual level).

The technical artifacts of the _Releasable Outcome_ are:

- a docker image in the docker registry
- a GitHub pre-release

### Deploy into Production

The _Releasable Outcome_ can be deployed into Production automatically or
manually. If it is deployed automatically the GitHub pre-release is updated
to a GitHub release.

To deploy manually take any GitHub pre-release and change it into a release
via the GitHub UI.

</details>

## Additional resources

- [Sops](https://github.com/getsops/sops) based
  [Secret Manager](https://github.com/metro-digital-inner-source/secrets-manager).
- [Kustomize plugin](https://github.com/metro-digital/kustomize-google-secret-manager)
  to process secrets from
  [Google Secret Manager](https://cloud.google.com/secret-manager) in WaaS.
- [Kenv](https://github.com/metro-digital/kenv) used in test setup for WaaS.
- Terraform module
  [cf-projectcfg](https://github.com/metro-digital/terraform-google-cf-projectcfg)
  which helps you getting started with project setup.

## WaaS schema

```yaml
apiVersion: waas/v2
metadata:
  name: service-name                              # name used in the kubernetes manifests rendered with
customBuildWorkflow:                              # (optional) define your own custom build workflow
  filename: <workflow-name>                       # name of the workflow file to define your custom workflow steps, e.g., custom-build.yaml
  cacheOutput:                                    # (optional) option to cache the files from a defined path. It uses `actions/cache/save@v3` to
                                                  # cache the output and `actions/cache/restore@v3` to restore the cached output in commit-cycle
                                                  # workflow
    path: <relative-path-from-working-dir>        # Relative path from working directory to cache the files that can be restored in commit-cycle
                                                  # workflow
    key: <an-explicit-key-for-a-cache-entry>      # (optional) (default: '${{ runner.os }}-${{ github.repository_id }}-${{ github.sha }}-${{ github.run_id }}-${{ github.run_attempt }}')
                                                  # The key used for cache entry. For more details look at the caching action, https://github.com/actions/cache
    restoreKeys: <keys-to-use-to-resotre-cache>   # (optional when `key` is not provided) (default: '${{ runner.os }}-${{ github.repository_id }}-${{ github.sha }}-${{ github.run_id }}')
                                                  # Keys used to find the cached entry. For more details look at the caching action, https://github.com/actions/cache
profiles:
  - name: build                                   # a unique profile name, but `build` makes most sense
                                                  # the whole build profile is optional
    environment: build                            # the type of an environment that the profile belongs to
                                                  # the build profile is used to configure secretsProvider during
                                                  # the build step and configure which builder should build the service
    containerImageFloatingTag: <tag-name>         # an additional floating tag assigned to the container image(for example, can be used
                                                  # while defining clean up policies in the contianer registries)
    secretsProvider:                              # (optional) secrets provider to use for getting docker credentials
                                                  # Use either `sops` or `googleSecretManager`.
                                                  # It defaults to `sops` if the runtimeProvider in other profiles is `metro-runtime`
                                                  # secretsProvider cannot be used in combination with Google Cloud Build as builderProvider
      googleSecretManager:
        projectId: gcp-project-id                 # the GCP project ID hosting the google secret manager
      sops: {}
    builderProvider:                              # (optional) defaults to `local`
                                                  # builder provider to use in the workflow for building the service
      local:                                      # use this to build on the localhost (= GitHub runner), supports only Docker
        service: docker
      gcp:                                        # use this to build using Google Cloud Build, this can only be used if the service
                                                  # is deployed to GCP runtimes for all environments
        service: cloud-build
        projectId: gcp-project-id                 # the GCP project ID to use cloud build service
        config:                                   # (optional) configure the builder, without config a buildpack is used
          builder: docker                         # which does a build by detecting the development technology
  - name: <name>                                  # a unique profile name, eg: "dev" or "prod"
    environment: (test|production|showcase)       # the type of an environment that the profile belongs to
                                                  # test:       environment used for testing (can be deployed automatically)
                                                  # production: only one prod environment    (can be deployed automatically)
                                                  # showcase:   we don't care                (can only be deployed manually)
    containerImageFloatingTag: <tag-name>         # an additional floating tag assigned to the container image(for example, can be used
                                                  # while defining clean up policies in the contianer registries)
    deploy: (auto|manual)                         # switch that allows to deploy manually
                                                  # to an environment by setting it to `manual`.
                                                  # defaults to `auto` for both 'test' and 'production' environments
                                                  # the 'showcase' environment ignores `deploy` switch
    runtimeProvider:                              # runtime provider to use in the workflow for deploying the service
      gcp:                                        # use this to deploy into GCP
        service: (gke|cloud-run)
        config:                                   # configuration only required for `cloud-run`
          kind: service
          serviceAccount: service-account-name    # GCP service account which cloud-run service should use at runtime
      metro:                                      # use this to deploy into metro-runtime
        service: kubernetes
    secretsProvider:                              # (optional) secrets provider to use in the workflow:
                                                  # without `secretsProvider` no support for secrets is created in the workflows.
                                                  # `sops` and `googleSecretManager` can be used together.
      googleSecretManager:
        projectId: gcp-project-id                 # the GCP project ID hosting the google secret manager
      sops: {}
```

## How to add notifications to WaaS?

Notifications for *success* or *failure* are no longer part of WaaS.
They have to be added outside of WaaS as separate workflows.

To ease to creation of such workflows we created workflow templates.

### How to access workflow templates (aka *starter workflows*)?

Please see this [GitHub documentation](https://docs.github.com/en/actions/using-workflows/using-starter-workflows)

Or for the impatient:

1. In your repository go to *Actions* and click *New workflow* button.
1. In the *Choose a workflow* page go to the section for METRO.digital
    and click on the *view all* link (same height as section heading!).
1. All workflow templates from M.d are showing up.
1. Choose the workflow you are interested in and click *Configure*.
1. Make modifications (if needed) and commit.

### Notifications via MS Teams

Choose the corresponding workflow template *Metro Digital: Send notifications via MS Teams*.

It assumes that you have a GitHub secret `MSTEAMS_WEBHOOK_URL` configured,
which contains the URL for the MS Teams incoming webhook.

See this Microsoft documentation for [creating webhooks](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).

### Notification via Email

Choose the corresponding workflow template *Metro Digital: Send notifications via Email*.

You only have to add the (list of) recipient(s).

The GitHub secrets `MD_EMAIL_SERVER_NAME` and `MD_EMAIL_SERVER_PORT` are automatically
added to your repository. They are configured to use our internal email server,
so that also METRO internal distribution lists should work (not tested!).
