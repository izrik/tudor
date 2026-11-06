# Version numbers

Releases are tagged `vX.Y` — two components, no patch number, as every tag in this repo has been.

**A missing patch number is implicitly zero.** `v1.0` and `1.0.0` are the same version, so a release can be referred to either way. This is also how Python itself compares them: under PEP 440, `Version('1.0') == Version('1.0.0')`.

Which component to bump follows [semver](https://semver.org/)'s rules as far as the two-component form allows: incompatible or removed behavior bumps the first, backward-compatible features and fixes the second. Versions before `v1.0` were a plain series and didn't claim semver.

# Cutting a release

Creating the Git tag and publishing a GitHub release do not require a Docker image build, manual smoke test, or image publication.

There is no version to edit in the repo. `build_docker.sh` passes the version to the Dockerfile as the `VERSION` build argument, which writes `__version__.py` into the image; outside the image, `run_local.sh` generates that file from `git describe`. Neither is checked in.

To create a new GitHub release for version `X.Y`:
 * Merge all relevant branches into `master`
 * Create a `prep-x.y` branch for the new version
   * In `CHANGELOG.md`, rename the `## [Unreleased]` heading to `## [vX.Y] - YYYY-MM-DD`, using the date the release is tagged, and start a fresh empty `## [Unreleased]` section above it. Add the `[vX.Y]` compare link at the bottom of the file and point `[Unreleased]` at the new tag.
   * Make any necessary minor fixes
   * Merge `prep-x.y` into `master`
 * Create a new release in GitHub.
   * The "Tag version" should be of the form `vx.y`
   * Include a release title summarizing the main changes or purpose of the release.
   * Take the description from the new version's section in `CHANGELOG.md`, which already lists the changes since the previous release.
   * Attach any binaries or files to the release, if warranted. But this isn't typical.

# Optional Docker image workflow

Building, manually testing, and publishing a Docker image are separate from publishing a GitHub release. These steps may be performed independently and are not prerequisites for creating the Git tag or GitHub release.

 * Check out the commit for the version you want to package (the `vX.Y` tag, if it already exists).
 * Build the image with a tag of the form `x.y`: `./build_docker.sh x.y`.
   * Pass the version explicitly, especially before the Git tag exists; otherwise `build_docker.sh` derives it from `git describe --tags`, which may produce a value like `0.16-48-g94205fd`.
 * Do any appropriate manual testing of the resulting `tudor:x.y` image before publishing the image.
 * To publish the image to Docker Hub, run `docker push izrik/tudor:x.y`. This publishes the image only; it does not create a Git tag or GitHub release.
