// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtb_muxprobe__pch.h"

//============================================================
// Constructors

Vtb_muxprobe::Vtb_muxprobe(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtb_muxprobe__Syms(contextp(), _vcname__, this)}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtb_muxprobe::Vtb_muxprobe(const char* _vcname__)
    : Vtb_muxprobe(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtb_muxprobe::~Vtb_muxprobe() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtb_muxprobe___024root___eval_debug_assertions(Vtb_muxprobe___024root* vlSelf);
#endif  // VL_DEBUG
void Vtb_muxprobe___024root___eval_static(Vtb_muxprobe___024root* vlSelf);
void Vtb_muxprobe___024root___eval_initial(Vtb_muxprobe___024root* vlSelf);
void Vtb_muxprobe___024root___eval_settle(Vtb_muxprobe___024root* vlSelf);
void Vtb_muxprobe___024root___eval(Vtb_muxprobe___024root* vlSelf);

void Vtb_muxprobe::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtb_muxprobe::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtb_muxprobe___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtb_muxprobe___024root___eval_static(&(vlSymsp->TOP));
        Vtb_muxprobe___024root___eval_initial(&(vlSymsp->TOP));
        Vtb_muxprobe___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtb_muxprobe___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtb_muxprobe::eventsPending() { return !vlSymsp->TOP.__VdlySched.empty() && !contextp()->gotFinish(); }

uint64_t Vtb_muxprobe::nextTimeSlot() { return vlSymsp->TOP.__VdlySched.nextTimeSlot(); }

//============================================================
// Utilities

const char* Vtb_muxprobe::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtb_muxprobe___024root___eval_final(Vtb_muxprobe___024root* vlSelf);

VL_ATTR_COLD void Vtb_muxprobe::final() {
    Vtb_muxprobe___024root___eval_final(&(vlSymsp->TOP));
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtb_muxprobe::hierName() const { return vlSymsp->name(); }
const char* Vtb_muxprobe::modelName() const { return "Vtb_muxprobe"; }
unsigned Vtb_muxprobe::threads() const { return 1; }
void Vtb_muxprobe::prepareClone() const { contextp()->prepareClone(); }
void Vtb_muxprobe::atClone() const {
    contextp()->threadPoolpOnClone();
}
