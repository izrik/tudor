To create a new release for version `X.Y`:
 * Merge all relevant branches into `master`
 * Create a `prep-x.y` branch for the new version
   * In `CHANGELOG.md`, rename the `## [Unreleased]` heading to `## [vX.Y] - YYYY-MM-DD`, using the date the release is tagged, and start a fresh empty `## [Unreleased]` section above it. Add the `[vX.Y]` compare link at the bottom of the file and point `[Unreleased]` at the new tag.
   * Make any necessary minor fixes
   * Merge `prep-x.y` into `master`
 * Build the docker image and do any appropriate manual testing. Give it a tag of the form `x.y`.
   * There is no version to edit in the repo. `build_docker.sh` passes the version to the Dockerfile as the `VERSION` build argument, which writes `__version__.py` into the image; outside the image, `run_local.sh` generates that file from `git describe`. Neither is checked in.
   * The tag doesn't exist yet at this point, so the version `build_docker.sh` derives from `git describe --tags` would be something like `0.16-48-g94205fd`. Pass it explicitly instead: `./build_docker.sh x.y`.
 * Create a new release in github.
   * The "Tag version" should be of the form `vx.y`
   * Include a release title summarizing the main changes or purpose of the release.
   * Take the description from the new version's section in `CHANGELOG.md`, which already lists the changes since the previous release.
   * Attach any binaries or files to the release, if warranted. But this isn't typical.
 * Push the docker image.
