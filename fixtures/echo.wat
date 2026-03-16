(module
  (type $func_t (func (param i32) (result i32)))
  (func $run (type $func_t) (param $input i32) (result i32)
    local.get $input
  )
  (export "run" (func $run))
)