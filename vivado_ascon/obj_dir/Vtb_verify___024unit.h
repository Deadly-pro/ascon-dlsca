// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_verify.h for the primary calling header

#ifndef VERILATED_VTB_VERIFY___024UNIT_H_
#define VERILATED_VTB_VERIFY___024UNIT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"


class Vtb_verify__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_verify___024unit final {
  public:

    // INTERNAL VARIABLES
    Vtb_verify__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_verify___024unit();
    ~Vtb_verify___024unit();
    void ctor(Vtb_verify__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtb_verify___024unit);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
