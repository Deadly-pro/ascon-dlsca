// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTB_DUMP__SYMS_H_
#define VERILATED_VTB_DUMP__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vtb_dump.h"

// INCLUDE MODULE CLASSES
#include "Vtb_dump___024root.h"
#include "Vtb_dump___024unit.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vtb_dump__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtb_dump* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtb_dump___024root             TOP;

    // CONSTRUCTORS
    Vtb_dump__Syms(VerilatedContext* contextp, const char* namep, Vtb_dump* modelp);
    ~Vtb_dump__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard
