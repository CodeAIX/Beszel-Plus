package beszel

// Keep Version as the upstream protocol version: capability checks use semver.
// The fork's display/release identity is set separately by the image builder.
const IsPlus = true

var PlusVersion = "dev"
var PlusCommit = "unknown"
