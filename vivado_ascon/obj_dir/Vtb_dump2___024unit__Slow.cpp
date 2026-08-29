// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_dump2.h for the primary calling header

#include "Vtb_dump2__pch.h"

void Vtb_dump2___024unit___ctor_var_reset(Vtb_dump2___024unit* vlSelf);

Vtb_dump2___024unit::Vtb_dump2___024unit() = default;
Vtb_dump2___024unit::~Vtb_dump2___024unit() = default;

void Vtb_dump2___024unit::ctor(Vtb_dump2__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
    Vtb_dump2___024unit___ctor_var_reset(this);
}

void Vtb_dump2___024unit::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtb_dump2___024unit::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
