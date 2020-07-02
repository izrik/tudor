To create a new release for version `X.Y`:
 * Merge all relevant branches into `master`
 * Create a `prep-x.y` branch for the new version
   * Update the `__version__`
   * Make any necessary minor fixes
   * Merge `prep-x.y` into `master`
 * Build the docker image and do any appropriate manual testing. Give it a tag of the form `x.y`.
 * Create a new release in github.
   * The "Tag version" should be of the form `vx.y`
   * Include a release title summarizing the main changes or purpose of the release.
   * Write a description that lists the changes since the previous release.
   * Attach any binaries or files to the release, if warranted. But this isn't typical.
 * Push the docker image.
