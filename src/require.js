// My own implementation of a basic 'require' functionality

// The module builder must append this to a file with the modules defined
// in `var modules : String => Function`.
// The module is a function which takes a function require and an exports map.

function LoopError(module) {
  this.module = module
}

function UndefinedModule(module) {
  this.module = module
}

var module_cache = {}

function require(module) {
  if (module in modules) {
    if (module in module_cache) {
      cached = module_cache[module]

      if (cached == undefined) {
        throw new LoopError(module)
      }

      return cached
    } else {
      var exports = new Object
      module_cache[module] = undefined
      modules[module](require, exports)
      module_cache[module] = exports
      return exports;
    }
  }

  throw new UndefinedModule(module)
}
