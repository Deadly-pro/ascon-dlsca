// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtb_dump__pch.h"

//============================================================
// Constructors

Vtb_dump::Vtb_dump(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtb_dump__Syms(contextp(), _vcname__, this)}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtb_dump::Vtb_dump(const char* _vcname__)
    : Vtb_dump(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtb_dump::~Vtb_dump() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtb_dump___024root___eval_debug_assertions(Vtb_dump___024root* vlSelf);
#endif  // VL_DEBUG
void Vtb_dump___024root___eval_static(Vtb_dump___024root* vlSelf);
void Vtb_dump___024root___eval_initial(Vtb_dump___024root* vlSelf);
void Vtb_dump___024root___eval_settle(Vtb_dump___024root* vlSelf);
void Vtb_dump___024root___eval(Vtb_dump___024root* vlSelf);

void Vtb_dump::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtb_dump::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtb_dump___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtb_dump___024root___eval_static(&(vlSymsp->TOP));
        Vtb_dump___024root___eval_initial(&(vlSymsp->TOP));
        Vtb_dump___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtb_dump___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtb_dump::eventsPending() { return !vlSymsp->TOP.__VdlySched.empty() && !contextp()->gotFinish(); }

uint64_t Vtb_dump::nextTimeSlot() { return vlSymsp->TOP.__VdlySched.nextTimeSlot(); }

//============================================================
// Utilities

const char* Vtb_dump::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtb_dump___024root___eval_final(Vtb_dump___024root* vlSelf);

VL_ATTR_COLD void Vtb_dump::final() {
    Vtb_dump___024root___eval_final(&(vlSymsp->TOP));
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtb_dump::hierName() const { return vlSymsp->name(); }
const char* Vtb_dump::modelName() const { return "Vtb_dump"; }
unsigned Vtb_dump::threads() const { return 1; }
void Vtb_dump::prepareClone() const { contextp()->prepareClone(); }
void Vtb_dump::atClone() const {
    contextp()->threadPoolpOnClone();
}
