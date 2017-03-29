// My own implementation of a basic 'require' functionality

// The module builder must append this to a file with the modules defined
// in `var modules : String => Function`.
// The module is a function which takes a function require and an exports map.

function require(module) {
  if (module in modules) {
    var exports = new Object
    modules[module](require, exports);
    return exports;
  }

  throw "No such module: " + module;
}
