// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_muxprobe.h for the primary calling header

#include "Vtb_muxprobe__pch.h"

void Vtb_muxprobe___024unit___ctor_var_reset(Vtb_muxprobe___024unit* vlSelf);

Vtb_muxprobe___024unit::Vtb_muxprobe___024unit() = default;
Vtb_muxprobe___024unit::~Vtb_muxprobe___024unit() = default;

void Vtb_muxprobe___024unit::ctor(Vtb_muxprobe__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
    Vtb_muxprobe___024unit___ctor_var_reset(this);
}

void Vtb_muxprobe___024unit::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtb_muxprobe___024unit::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
