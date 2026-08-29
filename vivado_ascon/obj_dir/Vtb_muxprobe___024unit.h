// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_muxprobe.h for the primary calling header

#ifndef VERILATED_VTB_MUXPROBE___024UNIT_H_
#define VERILATED_VTB_MUXPROBE___024UNIT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"


class Vtb_muxprobe__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_muxprobe___024unit final {
  public:

    // INTERNAL VARIABLES
    Vtb_muxprobe__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_muxprobe___024unit();
    ~Vtb_muxprobe___024unit();
    void ctor(Vtb_muxprobe__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtb_muxprobe___024unit);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
