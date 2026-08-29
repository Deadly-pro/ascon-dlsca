// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTB_DUMP2__SYMS_H_
#define VERILATED_VTB_DUMP2__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vtb_dump2.h"

// INCLUDE MODULE CLASSES
#include "Vtb_dump2___024root.h"
#include "Vtb_dump2___024unit.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vtb_dump2__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtb_dump2* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtb_dump2___024root            TOP;

    // CONSTRUCTORS
    Vtb_dump2__Syms(VerilatedContext* contextp, const char* namep, Vtb_dump2* modelp);
    ~Vtb_dump2__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard
