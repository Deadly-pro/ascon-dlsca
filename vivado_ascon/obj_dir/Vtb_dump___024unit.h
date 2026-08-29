// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_dump.h for the primary calling header

#ifndef VERILATED_VTB_DUMP___024UNIT_H_
#define VERILATED_VTB_DUMP___024UNIT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"


class Vtb_dump__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_dump___024unit final {
  public:

    // INTERNAL VARIABLES
    Vtb_dump__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_dump___024unit();
    ~Vtb_dump___024unit();
    void ctor(Vtb_dump__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtb_dump___024unit);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
