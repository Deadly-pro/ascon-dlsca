// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_verify.h for the primary calling header

#include "Vtb_verify__pch.h"

void Vtb_verify___024unit___ctor_var_reset(Vtb_verify___024unit* vlSelf);

Vtb_verify___024unit::Vtb_verify___024unit() = default;
Vtb_verify___024unit::~Vtb_verify___024unit() = default;

void Vtb_verify___024unit::ctor(Vtb_verify__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
    Vtb_verify___024unit___ctor_var_reset(this);
}

void Vtb_verify___024unit::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtb_verify___024unit::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
