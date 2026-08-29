// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtb_verify__pch.h"

//============================================================
// Constructors

Vtb_verify::Vtb_verify(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtb_verify__Syms(contextp(), _vcname__, this)}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtb_verify::Vtb_verify(const char* _vcname__)
    : Vtb_verify(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtb_verify::~Vtb_verify() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtb_verify___024root___eval_debug_assertions(Vtb_verify___024root* vlSelf);
#endif  // VL_DEBUG
void Vtb_verify___024root___eval_static(Vtb_verify___024root* vlSelf);
void Vtb_verify___024root___eval_initial(Vtb_verify___024root* vlSelf);
void Vtb_verify___024root___eval_settle(Vtb_verify___024root* vlSelf);
void Vtb_verify___024root___eval(Vtb_verify___024root* vlSelf);

void Vtb_verify::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtb_verify::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtb_verify___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtb_verify___024root___eval_static(&(vlSymsp->TOP));
        Vtb_verify___024root___eval_initial(&(vlSymsp->TOP));
        Vtb_verify___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtb_verify___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtb_verify::eventsPending() { return !vlSymsp->TOP.__VdlySched.empty() && !contextp()->gotFinish(); }

uint64_t Vtb_verify::nextTimeSlot() { return vlSymsp->TOP.__VdlySched.nextTimeSlot(); }

//============================================================
// Utilities

const char* Vtb_verify::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtb_verify___024root___eval_final(Vtb_verify___024root* vlSelf);

VL_ATTR_COLD void Vtb_verify::final() {
    Vtb_verify___024root___eval_final(&(vlSymsp->TOP));
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtb_verify::hierName() const { return vlSymsp->name(); }
const char* Vtb_verify::modelName() const { return "Vtb_verify"; }
unsigned Vtb_verify::threads() const { return 1; }
void Vtb_verify::prepareClone() const { contextp()->prepareClone(); }
void Vtb_verify::atClone() const {
    contextp()->threadPoolpOnClone();
}
