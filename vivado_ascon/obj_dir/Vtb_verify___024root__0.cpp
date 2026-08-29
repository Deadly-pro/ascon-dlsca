// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_verify.h for the primary calling header

#include "Vtb_verify__pch.h"

VlCoroutine Vtb_verify___024root___eval_initial__TOP__Vtiming__0(Vtb_verify___024root* vlSelf);
VlCoroutine Vtb_verify___024root___eval_initial__TOP__Vtiming__1(Vtb_verify___024root* vlSelf);

void Vtb_verify___024root___eval_initial(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_initial\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_verify___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_verify___024root___eval_initial__TOP__Vtiming__1(vlSelf);
}

void Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription);
void Vtb_verify___024root____VbeforeTrig_hae8e2579__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription);
void Vtb_verify___024root____VbeforeTrig_h096fd0ca__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription);
void Vtb_verify___024root____VbeforeTrig_h8d3cb2b4__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription);

VlCoroutine Vtb_verify___024root___eval_initial__TOP__Vtiming__0(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_verify__DOT__errors;
    tb_verify__DOT__errors = 0;
    IData/*31:0*/ tb_verify__DOT__unnamedblk4__DOT__i;
    tb_verify__DOT__unnamedblk4__DOT__i = 0;
    Vtb_verify_tb_verify__DOT__vector_t__struct__0 __Vtask_tb_verify__DOT__run_vector__0__v;
    __Vtask_tb_verify__DOT__run_vector__0__v.__PVT__key1 = 0;
    __Vtask_tb_verify__DOT__run_vector__0__v.__PVT__key2 = 0;
    __Vtask_tb_verify__DOT__run_vector__0__v.__PVT__nonce1 = 0;
    __Vtask_tb_verify__DOT__run_vector__0__v.__PVT__nonce2 = 0;
    VL_ZERO_W(128, __Vtask_tb_verify__DOT__run_vector__0__v.__PVT__exp);
    IData/*31:0*/ __Vtask_tb_verify__DOT__run_vector__0__idx;
    __Vtask_tb_verify__DOT__run_vector__0__idx = 0;
    IData/*31:0*/ __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_1__DOT____Vrepeat0;
    __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    IData/*31:0*/ __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_2__DOT____Vrepeat1;
    __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_2__DOT____Vrepeat1 = 0;
    QData/*63:0*/ __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout;
    __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout = 0;
    QData/*63:0*/ __Vfunc_tb_verify__DOT__rev_bytes64__3__x;
    __Vfunc_tb_verify__DOT__rev_bytes64__3__x = 0;
    IData/*31:0*/ __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout;
    __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_verify__DOT__rev_bytes32__4__x;
    __Vfunc_tb_verify__DOT__rev_bytes32__4__x = 0;
    IData/*31:0*/ __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout;
    __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_verify__DOT__rev_bytes32__5__x;
    __Vfunc_tb_verify__DOT__rev_bytes32__5__x = 0;
    VlWide<3>/*95:0*/ __Vtemp_1;
    // Body
    vlSymsp->_vm_contextp__->dumpfile("tb_verify.fst"s);
    VL_PRINTF_MT("-Info: tb_verify.sv:185: $dumpvar ignored, as Verilated without --trace\n");
    tb_verify__DOT__errors = 0U;
    vlSelfRef.tb_verify__DOT__reset_n = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x0000000000004e20ULL, 
                                         nullptr, "tb_verify.sv", 
                                         192);
    vlSelfRef.tb_verify__DOT__reset_n = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x0000000000002710ULL, 
                                         nullptr, "tb_verify.sv", 
                                         195);
    tb_verify__DOT__unnamedblk4__DOT__i = 0U;
    while (VL_GTS_III(32, 5U, tb_verify__DOT__unnamedblk4__DOT__i)) {
        VL_WRITEF_NX("=== vector %0d ===\n",0,32,tb_verify__DOT__unnamedblk4__DOT__i);
        __Vtask_tb_verify__DOT__run_vector__0__idx 
            = tb_verify__DOT__unnamedblk4__DOT__i;
        __Vtask_tb_verify__DOT__run_vector__0__v = vlSelfRef.tb_verify__DOT__vectors
            [((4U >= (7U & tb_verify__DOT__unnamedblk4__DOT__i))
               ? (7U & tb_verify__DOT__unnamedblk4__DOT__i)
               : 0U)];
        __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
        __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_2__DOT____Vrepeat1 = 0;
        vlSelfRef.tb_verify__DOT__key1 = __Vtask_tb_verify__DOT__run_vector__0__v
            .__PVT__key1;
        vlSelfRef.tb_verify__DOT__key2 = __Vtask_tb_verify__DOT__run_vector__0__v
            .__PVT__key2;
        vlSelfRef.tb_verify__DOT__nonce1 = __Vtask_tb_verify__DOT__run_vector__0__v
            .__PVT__nonce1;
        vlSelfRef.tb_verify__DOT__nonce2 = __Vtask_tb_verify__DOT__run_vector__0__v
            .__PVT__nonce2;
        VL_ASSIGN_W(128, vlSelfRef.tb_verify__DOT__exp_ro, __Vtask_tb_verify__DOT__run_vector__0__v
                    .__PVT__exp);
        vlSelfRef.tb_verify__DOT__start = 1U;
        vlSelfRef.tb_verify__DOT__load_data = 1U;
        __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_1__DOT____Vrepeat0 = 4U;
        while (VL_LTS_III(32, 0U, __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
            Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(vlSelf, 
                                                             "@(posedge tb_verify.clk)");
            co_await vlSelfRef.__VtrigSched_h2e47bcf5__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_verify.clk)", 
                                                                 "tb_verify.sv", 
                                                                 129);
            __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_1__DOT____Vrepeat0 
                = (__Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_1__DOT____Vrepeat0 
                   - (IData)(1U));
        }
        vlSelfRef.tb_verify__DOT__start = 0U;
        vlSelfRef.tb_verify__DOT__load_data = 0U;
        while (vlSelfRef.tb_verify__DOT__uut__DOT__buf_full) {
            Vtb_verify___024root____VbeforeTrig_hae8e2579__0(vlSelf, 
                                                             "@( (~ tb_verify.uut.buf_full))");
            co_await vlSelfRef.__VtrigSched_hae8e2579__0.trigger(1U, 
                                                                 nullptr, 
                                                                 "@( (~ tb_verify.uut.buf_full))", 
                                                                 "tb_verify.sv", 
                                                                 134);
        }
        Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(vlSelf, 
                                                         "@(posedge tb_verify.clk)");
        co_await vlSelfRef.__VtrigSched_h2e47bcf5__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_verify.clk)", 
                                                             "tb_verify.sv", 
                                                             135);
        vlSelfRef.tb_verify__DOT__valid_data_in = 1U;
        vlSelfRef.tb_verify__DOT__last_block = 1U;
        vlSelfRef.tb_verify__DOT__EOT = 0U;
        vlSelfRef.tb_verify__DOT__valid_bytes = 4U;
        vlSelfRef.tb_verify__DOT__data_in[0U] = 0U;
        vlSelfRef.tb_verify__DOT__data_in[1U] = 0U;
        vlSelfRef.tb_verify__DOT__data_in[2U] = 0U;
        vlSelfRef.tb_verify__DOT__data_in[3U] = 0U;
        Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(vlSelf, 
                                                         "@(posedge tb_verify.clk)");
        co_await vlSelfRef.__VtrigSched_h2e47bcf5__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_verify.clk)", 
                                                             "tb_verify.sv", 
                                                             137);
        vlSelfRef.tb_verify__DOT__valid_data_in = 0U;
        while (vlSelfRef.tb_verify__DOT__uut__DOT__buf_full) {
            Vtb_verify___024root____VbeforeTrig_hae8e2579__0(vlSelf, 
                                                             "@( (~ tb_verify.uut.buf_full))");
            co_await vlSelfRef.__VtrigSched_hae8e2579__0.trigger(1U, 
                                                                 nullptr, 
                                                                 "@( (~ tb_verify.uut.buf_full))", 
                                                                 "tb_verify.sv", 
                                                                 141);
        }
        Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(vlSelf, 
                                                         "@(posedge tb_verify.clk)");
        co_await vlSelfRef.__VtrigSched_h2e47bcf5__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_verify.clk)", 
                                                             "tb_verify.sv", 
                                                             142);
        vlSelfRef.tb_verify__DOT__valid_data_in = 1U;
        vlSelfRef.tb_verify__DOT__last_block = 1U;
        vlSelfRef.tb_verify__DOT__EOT = 1U;
        vlSelfRef.tb_verify__DOT__valid_bytes = 4U;
        vlSelfRef.tb_verify__DOT__data_in[0U] = 0U;
        vlSelfRef.tb_verify__DOT__data_in[1U] = 0U;
        vlSelfRef.tb_verify__DOT__data_in[2U] = 0U;
        vlSelfRef.tb_verify__DOT__data_in[3U] = 0U;
        while ((1U & (~ ((~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window)) 
                         & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__msg_win_q))))) {
            Vtb_verify___024root____VbeforeTrig_h096fd0ca__0(vlSelf, 
                                                             "@( ((~ tb_verify.uut.in_msg_window) & tb_verify.uut.msg_win_q))");
            co_await vlSelfRef.__VtrigSched_h096fd0ca__0.trigger(1U, 
                                                                 nullptr, 
                                                                 "@( ((~ tb_verify.uut.in_msg_window) & tb_verify.uut.msg_win_q))", 
                                                                 "tb_verify.sv", 
                                                                 146);
        }
        Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(vlSelf, 
                                                         "@(posedge tb_verify.clk)");
        co_await vlSelfRef.__VtrigSched_h2e47bcf5__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_verify.clk)", 
                                                             "tb_verify.sv", 
                                                             147);
        vlSelfRef.tb_verify__DOT__latched_ct[0U] = (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__ct_lo);
        vlSelfRef.tb_verify__DOT__latched_ct[1U] = (IData)(
                                                           (vlSelfRef.tb_verify__DOT__uut__DOT__ct_lo 
                                                            >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__latched_ct[2U] = (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__ct_hi);
        vlSelfRef.tb_verify__DOT__latched_ct[3U] = (IData)(
                                                           (vlSelfRef.tb_verify__DOT__uut__DOT__ct_hi 
                                                            >> 0x00000020U));
        VL_WRITEF_NX("CT = %032x\n",0,128,vlSelfRef.tb_verify__DOT__latched_ct.data());
        vlSelfRef.tb_verify__DOT__valid_data_in = 0U;
        while ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse)))) {
            Vtb_verify___024root____VbeforeTrig_h8d3cb2b4__0(vlSelf, 
                                                             "@( tb_verify.uut.ready_tag_pulse)");
            co_await vlSelfRef.__VtrigSched_h8d3cb2b4__0.trigger(1U, 
                                                                 nullptr, 
                                                                 "@( tb_verify.uut.ready_tag_pulse)", 
                                                                 "tb_verify.sv", 
                                                                 154);
        }
        Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(vlSelf, 
                                                         "@(posedge tb_verify.clk)");
        co_await vlSelfRef.__VtrigSched_h2e47bcf5__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_verify.clk)", 
                                                             "tb_verify.sv", 
                                                             155);
        vlSelfRef.tb_verify__DOT__latched_tag2 = vlSelfRef.tb_verify__DOT__uut__DOT__tg2_r;
        vlSelfRef.tb_verify__DOT__latched_tag1 = vlSelfRef.tb_verify__DOT__uut__DOT__tg1_r;
        VL_WRITEF_NX("TAG = %016x%016x\n",0,64,vlSelfRef.tb_verify__DOT__latched_tag2,
                     64,vlSelfRef.tb_verify__DOT__latched_tag1);
        vlSelfRef.tb_verify__DOT__done_flag = 0U;
        __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_2__DOT____Vrepeat1 = 0x000003e8U;
        while (VL_LTS_III(32, 0U, __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_2__DOT____Vrepeat1)) {
            Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(vlSelf, 
                                                             "@(posedge tb_verify.clk)");
            co_await vlSelfRef.__VtrigSched_h2e47bcf5__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_verify.clk)", 
                                                                 "tb_verify.sv", 
                                                                 162);
            if (vlSelfRef.tb_verify__DOT__uut__DOT__done_r) {
                vlSelfRef.tb_verify__DOT__done_flag = 1U;
            }
            __Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_2__DOT____Vrepeat1 
                = (__Vtask_tb_verify__DOT__run_vector__0__tb_verify__DOT__unnamedblk1_2__DOT____Vrepeat1 
                   - (IData)(1U));
        }
        if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__done_flag)))))) {
            VL_WRITEF_NX("FAIL v%0d: core never asserted done\n",0,
                         32,__Vtask_tb_verify__DOT__run_vector__0__idx);
            tb_verify__DOT__errors = ((IData)(1U) + tb_verify__DOT__errors);
        }
        VL_CONCAT_WQI(96,64,32, __Vtemp_1, ([&]() {
                    __Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                        = vlSelfRef.tb_verify__DOT__latched_tag1;
                    __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout = 0;
                    __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout 
                        = ((0xffffffffff000000ULL & __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout) 
                           | (IData)((IData)(((0x00ff0000U 
                                               & ((IData)(
                                                          (__Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                                                           >> 0x28U)) 
                                                  << 0x00000010U)) 
                                              | ((0x0000ff00U 
                                                  & ((IData)(
                                                             (__Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                                                              >> 0x30U)) 
                                                     << 8U)) 
                                                 | (0x000000ffU 
                                                    & (IData)(
                                                              (__Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                                                               >> 0x38U))))))));
                    __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout 
                        = ((0xffff000000ffffffULL & __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout) 
                           | ((QData)((IData)(((0x00ff0000U 
                                                & ((IData)(
                                                           (__Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                                                            >> 0x10U)) 
                                                   << 0x00000010U)) 
                                               | ((0x0000ff00U 
                                                   & ((IData)(
                                                              (__Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                                                               >> 0x18U)) 
                                                      << 8U)) 
                                                  | (0x000000ffU 
                                                     & (IData)(
                                                               (__Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                                                                >> 0x20U))))))) 
                              << 0x00000018U));
                    __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout 
                        = ((0x0000ffffffffffffULL & __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout) 
                           | ((QData)((IData)(((0x0000ff00U 
                                                & ((IData)(__Vfunc_tb_verify__DOT__rev_bytes64__3__x) 
                                                   << 8U)) 
                                               | (0x000000ffU 
                                                  & (IData)(
                                                            (__Vfunc_tb_verify__DOT__rev_bytes64__3__x 
                                                             >> 8U)))))) 
                              << 0x00000030U));
                }(), __Vfunc_tb_verify__DOT__rev_bytes64__3__Vfuncout), 
                      ([&]() {
                    __Vfunc_tb_verify__DOT__rev_bytes32__4__x 
                        = (IData)(vlSelfRef.tb_verify__DOT__latched_tag2);
                    __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout = 0;
                    __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout 
                        = ((0xff000000U & __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout) 
                           | ((0x00ff0000U & (__Vfunc_tb_verify__DOT__rev_bytes32__4__x 
                                              << 8U)) 
                              | ((0x0000ff00U & (__Vfunc_tb_verify__DOT__rev_bytes32__4__x 
                                                 >> 8U)) 
                                 | (__Vfunc_tb_verify__DOT__rev_bytes32__4__x 
                                    >> 0x18U))));
                    __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout 
                        = ((0x00ffffffU & __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout) 
                           | (__Vfunc_tb_verify__DOT__rev_bytes32__4__x 
                              << 0x00000018U));
                }(), __Vfunc_tb_verify__DOT__rev_bytes32__4__Vfuncout));
        VL_CONCAT_WWI(128,96,32, vlSelfRef.tb_verify__DOT__simulated_ro, __Vtemp_1, 
                      ([&]() {
                    __Vfunc_tb_verify__DOT__rev_bytes32__5__x 
                        = vlSelfRef.tb_verify__DOT__latched_ct[0U];
                    __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout = 0;
                    __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout 
                        = ((0xff000000U & __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout) 
                           | ((0x00ff0000U & (__Vfunc_tb_verify__DOT__rev_bytes32__5__x 
                                              << 8U)) 
                              | ((0x0000ff00U & (__Vfunc_tb_verify__DOT__rev_bytes32__5__x 
                                                 >> 8U)) 
                                 | (__Vfunc_tb_verify__DOT__rev_bytes32__5__x 
                                    >> 0x18U))));
                    __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout 
                        = ((0x00ffffffU & __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout) 
                           | (__Vfunc_tb_verify__DOT__rev_bytes32__5__x 
                              << 0x00000018U));
                }(), __Vfunc_tb_verify__DOT__rev_bytes32__5__Vfuncout));
        VL_WRITEF_NX("SIM readback = %032x\n",0,128,
                     vlSelfRef.tb_verify__DOT__simulated_ro.data());
        if ((0U == ((((vlSelfRef.tb_verify__DOT__simulated_ro[0U] 
                       ^ vlSelfRef.tb_verify__DOT__exp_ro[0U]) 
                      | (vlSelfRef.tb_verify__DOT__simulated_ro[1U] 
                         ^ vlSelfRef.tb_verify__DOT__exp_ro[1U])) 
                     | (vlSelfRef.tb_verify__DOT__simulated_ro[2U] 
                        ^ vlSelfRef.tb_verify__DOT__exp_ro[2U])) 
                    | (vlSelfRef.tb_verify__DOT__simulated_ro[3U] 
                       ^ vlSelfRef.tb_verify__DOT__exp_ro[3U])))) {
            VL_WRITEF_NX("PASS v%0d: simulation matches expected readback\n",0,
                         32,__Vtask_tb_verify__DOT__run_vector__0__idx);
        } else {
            VL_WRITEF_NX("FAIL v%0d: sim=%032x exp=%032x\n",0,
                         32,__Vtask_tb_verify__DOT__run_vector__0__idx,
                         128,vlSelfRef.tb_verify__DOT__simulated_ro.data(),
                         128,vlSelfRef.tb_verify__DOT__exp_ro.data());
            tb_verify__DOT__errors = ((IData)(1U) + tb_verify__DOT__errors);
        }
        tb_verify__DOT__unnamedblk4__DOT__i = ((IData)(1U) 
                                               + tb_verify__DOT__unnamedblk4__DOT__i);
    }
    if ((0U == tb_verify__DOT__errors)) {
        VL_WRITEF_NX("ALL 5 VECTORS PASS\n",0);
    } else {
        VL_WRITEF_NX("FAILURES: %0d/5\n",0,32,tb_verify__DOT__errors);
    }
    VL_FINISH_MT("tb_verify.sv", 207, "");
    co_return;
}

VlCoroutine Vtb_verify___024root___eval_initial__TOP__Vtiming__1(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "tb_verify.sv", 
                                             68);
        vlSelfRef.tb_verify__DOT__clk = (1U & (~ (IData)(vlSelfRef.tb_verify__DOT__clk)));
    }
    co_return;
}

void Vtb_verify___024root___eval_triggers_vec__act(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_triggers_vec__act\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __Vtrigprevexpr_h36b9350c__0;
    __Vtrigprevexpr_h36b9350c__0 = 0;
    CData/*0:0*/ __Vtrigprevexpr_h9dc7e85d__0;
    __Vtrigprevexpr_h9dc7e85d__0 = 0;
    // Body
    __Vtrigprevexpr_h36b9350c__0 = (1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full)));
    __Vtrigprevexpr_h9dc7e85d__0 = ((~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window)) 
                                    & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__msg_win_q));
    vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                    (((((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse) 
                                                        != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__ready_tag_pulse__0)) 
                                                       << 6U) 
                                                      | ((((IData)(__Vtrigprevexpr_h9dc7e85d__0) 
                                                           != (IData)(vlSelfRef.__Vtrigprevexpr_h9dc7e85d__1)) 
                                                          << 5U) 
                                                         | (((IData)(__Vtrigprevexpr_h36b9350c__0) 
                                                             != (IData)(vlSelfRef.__Vtrigprevexpr_h36b9350c__1)) 
                                                            << 4U))) 
                                                     | (((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                          << 3U) 
                                                         | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_rst) 
                                                             & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__core_rst__0))) 
                                                            << 2U)) 
                                                        | ((((~ (IData)(vlSelfRef.tb_verify__DOT__reset_n)) 
                                                             & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__reset_n__0)) 
                                                            << 1U) 
                                                           | ((IData)(vlSelfRef.tb_verify__DOT__clk) 
                                                              & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__clk__0))))))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__clk__0 
        = vlSelfRef.tb_verify__DOT__clk;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__reset_n__0 
        = vlSelfRef.tb_verify__DOT__reset_n;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__core_rst__0 
        = vlSelfRef.tb_verify__DOT__uut__DOT__core_rst;
    vlSelfRef.__Vtrigprevexpr_h36b9350c__1 = __Vtrigprevexpr_h36b9350c__0;
    vlSelfRef.__Vtrigprevexpr_h9dc7e85d__1 = __Vtrigprevexpr_h9dc7e85d__0;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__ready_tag_pulse__0 
        = vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse;
}

bool Vtb_verify___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___trigger_anySet__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

extern const VlWide<10>/*319:0*/ Vtb_verify__ConstPool__CONST_hab76c978_0;

void Vtb_verify___024root___act_comb__TOP__0(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___act_comb__TOP__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_verify__DOT__uut__DOT__core_bdi;
    tb_verify__DOT__uut__DOT__core_bdi = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__auth_d;
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d;
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx;
    tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad;
    tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad = 0;
    // Body
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[0U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[1U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[2U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[3U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U];
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_key) {
        VL_ASSIGNSEL_WQ(128, 64, (0x0000007fU & VL_SHIFTL_III(7,32,32, 
                                                              (1U 
                                                               & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                                  >> 2U)), 6U)), vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d, 
                        (((2U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                          & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__key_sel))
                          ? vlSelfRef.tb_verify__DOT__key2
                          : vlSelfRef.tb_verify__DOT__key1));
    }
    tb_verify__DOT__uut__DOT__core_bdi = 0ULL;
    if ((3U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        tb_verify__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__npub_sel)
                                               ? vlSelfRef.tb_verify__DOT__nonce2
                                               : vlSelfRef.tb_verify__DOT__nonce1);
    } else if (vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0) {
        tb_verify__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi)
                                               ? (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[3U])) 
                                                   << 0x00000020U) 
                                                  | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[2U])))
                                               : (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[1U])) 
                                                   << 0x00000020U) 
                                                  | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[0U]))));
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 
        (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
               >> 0x0000000aU));
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d 
        = (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 9U));
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 0U;
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d = 0U;
    }
    if (((0x0fU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         & (2U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))))) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d = 1U;
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d 
            = ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d) 
               & (tb_verify__DOT__uut__DOT__core_bdi 
                  == vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice));
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_d 
            = (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                >> 9U) & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d));
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0ULL;
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo = 0ULL;
    tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad = 0ULL;
    if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                              >> 1U)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo 
                        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice;
                }
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    if (((1U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
                         | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof))) {
                        vlSelfRef.__Vfunc_pad__8__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_pad__8__in 
                            = tb_verify__DOT__uut__DOT__core_bdi;
                        vlSelf->__Vfunc_pad__8__Vfuncout = 0;
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | (IData)((IData)(((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__8__in))
                                                   : 0U))));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((2U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 8U)))
                                                       : 
                                                      ((1U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((4U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x10U)))
                                                       : 
                                                      ((2U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((8U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x18U)))
                                                       : 
                                                      ((4U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000010U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x20U)))
                                                       : 
                                                      ((8U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000020U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x28U)))
                                                       : 
                                                      ((0x00000010U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000040U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x30U)))
                                                       : 
                                                      ((0x00000020U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000080U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x38U)))
                                                       : 
                                                      ((0x00000040U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000038U));
                        tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad 
                            = vlSelfRef.__Vfunc_pad__8__Vfuncout;
                        tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice 
                               ^ tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad);
                        vlSelfRef.__Vfunc_mask__9__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_mask__9__in1 
                            = tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx;
                        vlSelf->__Vfunc_mask__9__Vfuncout = 0;
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | (IData)((IData)(((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__9__in1))
                                                   : 0U))));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (2U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 8U)))
                                                    : 0U))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (4U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x10U)))
                                                    : 0U))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (8U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x18U)))
                                                    : 0U))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000010U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x20U)))
                                                    : 0U))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000020U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x28U)))
                                                    : 0U))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000040U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x30U)))
                                                    : 0U))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000080U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x38U)))
                                                    : 0U))) 
                                  << 0x00000038U));
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo 
                            = vlSelfRef.__Vfunc_mask__9__Vfuncout;
                    } else if ((2U == (0x0000000fU 
                                       & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
                        vlSelfRef.__Vfunc_pad2__10__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_pad2__10__in2 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice;
                        vlSelfRef.__Vfunc_pad2__10__in1 
                            = tb_verify__DOT__uut__DOT__core_bdi;
                        vlSelf->__Vfunc_pad2__10__Vfuncout = 0;
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | (IData)((IData)((0x000000ffU 
                                                  & ((1U 
                                                      & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                      ? (IData)(vlSelfRef.__Vfunc_pad2__10__in1)
                                                      : (IData)(vlSelfRef.__Vfunc_pad2__10__in2))))));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((2U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 8U)))
                                                       : 
                                                      ((1U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 8U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 8U)))))))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((4U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x10U)))
                                                       : 
                                                      ((2U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x10U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x10U)))))))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((8U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x18U)))
                                                       : 
                                                      ((4U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x18U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x18U)))))))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000010U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x20U)))
                                                       : 
                                                      ((8U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x20U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x20U)))))))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000020U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x28U)))
                                                       : 
                                                      ((0x00000010U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x28U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x28U)))))))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000040U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x30U)))
                                                       : 
                                                      ((0x00000020U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x30U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x30U)))))))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000080U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x38U)))
                                                       : 
                                                      ((0x00000040U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x38U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x38U)))))))) 
                                  << 0x00000038U));
                        tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad 
                            = vlSelfRef.__Vfunc_pad2__10__Vfuncout;
                        tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                            = tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad;
                        vlSelfRef.__Vfunc_mask__11__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_mask__11__in1 
                            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice 
                               ^ tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx);
                        vlSelf->__Vfunc_mask__11__Vfuncout = 0;
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | (IData)((IData)(((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__11__in1))
                                                   : 0U))));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (2U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 8U)))
                                                    : 0U))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (4U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x10U)))
                                                    : 0U))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (8U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x18U)))
                                                    : 0U))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000010U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x20U)))
                                                    : 0U))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000020U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x28U)))
                                                    : 0U))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000040U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x30U)))
                                                    : 0U))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000080U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x38U)))
                                                    : 0U))) 
                                  << 0x00000038U));
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo 
                            = vlSelfRef.__Vfunc_mask__11__Vfuncout;
                    }
                    if ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo = 0ULL;
                    }
                }
            }
        }
    } else if ((4U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                vlSelfRef.__Vfunc_pad__12__val = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                vlSelfRef.__Vfunc_pad__12__in = tb_verify__DOT__uut__DOT__core_bdi;
                vlSelf->__Vfunc_pad__12__Vfuncout = 0;
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffffffffff00ULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | (IData)((IData)(((1U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                           ? (0x000000ffU 
                                              & (IData)(vlSelfRef.__Vfunc_pad__12__in))
                                           : 0U))));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffffffff00ffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((2U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 8U)))
                                               : ((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 8U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffffff00ffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((4U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x10U)))
                                               : ((2U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000010U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffff00ffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((8U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x18U)))
                                               : ((4U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000018U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffff00ffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000010U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x20U)))
                                               : ((8U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000020U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffff00ffffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000020U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x28U)))
                                               : ((0x00000010U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000028U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xff00ffffffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000040U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x30U)))
                                               : ((0x00000020U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000030U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0x00ffffffffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000080U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x38U)))
                                               : ((0x00000040U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000038U));
                tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad 
                    = vlSelfRef.__Vfunc_pad__12__Vfuncout;
                tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                    = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice 
                       ^ tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad);
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                = tb_verify__DOT__uut__DOT__core_bdi;
        }
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d 
        = ((((((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_d) 
               << 5U) | (((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d) 
                          << 4U) | ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d) 
                                    << 3U))) | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_eot_d) 
                                                 << 2U) 
                                                | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d) 
                                                    << 1U) 
                                                   | (1U 
                                                      & ((~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done)) 
                                                         & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                                                            >> 5U)))))) 
            << 5U) | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d) 
                       << 4U) | (0x0000000fU & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done)
                                                 ? 
                                                ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                                  ? 1U
                                                  : 0U)
                                                 : (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[2U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[3U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U];
    if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9) 
         | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0 
            = tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx;
        if ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))) {
            VL_ASSIGNSEL_WQ(320, 64, (0x000001ffU & 
                                      VL_SHIFTL_III(9,32,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)), vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d, vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0);
        }
    }
    if (((7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         | (0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1 
            = (1ULL ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice);
        if ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))) {
            VL_ASSIGNSEL_WQ(320, 64, (0x000001ffU & 
                                      VL_SHIFTL_III(9,32,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)), vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d, vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1);
        }
    }
    if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) 
         & (((3U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                      ? 1U : 0U)) | (4U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                             ? 1U : 0U))) 
            | (5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                       ? 1U : 0U))))) {
        VL_ASSIGN_W(320, vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d, Vtb_verify__ConstPool__CONST_hab76c978_0);
        if ((1U & (~ VL_ONEHOT_I((((5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                            ? 1U : 0U)) 
                                   << 2U) | (((4U == 
                                               ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                                 ? 1U
                                                 : 0U)) 
                                              << 1U) 
                                             | (3U 
                                                == 
                                                ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                                  ? 1U
                                                  : 0U)))))))) {
            if ((0U != (((5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                  ? 1U : 0U)) << 2U) 
                        | (((4U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                     ? 1U : 0U)) << 1U) 
                           | (3U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                      ? 1U : 0U)))))) {
                if (VL_UNLIKELY((vlSymsp->_vm_contextp__->assertOn()))) {
                    VL_WRITEF_NX("[%0t] %%Error: ascon_core.sv:448: Assertion failed in %Ntb_verify.uut.u_core: unique case, but multiple matches found for '4'h%x'\n",0,
                                 64,VL_TIME_UNITED_Q(1000),
                                 -9,vlSymsp->name(),
                                 4,((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                     ? 1U : 0U));
                    VL_STOP_MT("rtl/ascon_core.sv", 448, "");
                }
            }
        }
        if ((3U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                     ? 1U : 0U))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0002U;
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000801U;
        } else if ((4U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                            ? 1U : 0U))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0003U;
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000800U;
        } else if ((5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                            ? 1U : 0U))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0004U;
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000800U;
        }
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x808c0001U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00001000U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[2U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[3U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U];
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                       ^ ((((QData)((IData)((0x0007ffffU 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                            << 0x0000002dU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                               >> 0x00000013U)) 
                          ^ (((QData)((IData)((0x0fffffffU 
                                               & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                              << 0x00000024U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                 >> 0x0000001cU)))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                        ^ ((((QData)((IData)((0x0007ffffU 
                                              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                             << 0x0000002dU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                >> 0x00000013U)) 
                           ^ (((QData)((IData)((0x0fffffffU 
                                                & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                               << 0x00000024U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                  >> 0x0000001cU)))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[2U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                       ^ (((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                            << 3U) | (QData)((IData)(
                                                     (7U 
                                                      & (IData)(
                                                                (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                 >> 0x0000003dU)))))) 
                          ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                              << 0x00000019U) | (QData)((IData)(
                                                                (0x01ffffffU 
                                                                 & (IData)(
                                                                           (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                            >> 0x00000027U)))))))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[3U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                        ^ (((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                             << 3U) | (QData)((IData)(
                                                      (7U 
                                                       & (IData)(
                                                                 (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                  >> 0x0000003dU)))))) 
                           ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                               << 0x00000019U) | (QData)((IData)(
                                                                 (0x01ffffffU 
                                                                  & (IData)(
                                                                            (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                             >> 0x00000027U)))))))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = (IData)(((~ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2) 
                       ^ ((((QData)((IData)((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                            << 0x0000003fU) | (0x7fffffffffffffffULL 
                                               & (~ 
                                                  (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                   >> 1U)))) 
                          ^ (((QData)((IData)((0x0000003fU 
                                               & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                              << 0x0000003aU) | (0x03ffffffffffffffULL 
                                                 & (~ 
                                                    (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                     >> 6U)))))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = (IData)((((~ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2) 
                        ^ ((((QData)((IData)((1U & 
                                              (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                             << 0x0000003fU) | (0x7fffffffffffffffULL 
                                                & (~ 
                                                   (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                    >> 1U)))) 
                           ^ (((QData)((IData)((0x0000003fU 
                                                & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                               << 0x0000003aU) | (0x03ffffffffffffffULL 
                                                  & (~ 
                                                     (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                      >> 6U)))))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                       ^ ((((QData)((IData)((0x000003ffU 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                            << 0x00000036U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                               >> 0x0000000aU)) 
                          ^ (((QData)((IData)((0x0001ffffU 
                                               & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                              << 0x0000002fU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                 >> 0x00000011U)))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                        ^ ((((QData)((IData)((0x000003ffU 
                                              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                             << 0x00000036U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                >> 0x0000000aU)) 
                           ^ (((QData)((IData)((0x0001ffffU 
                                                & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                               << 0x0000002fU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                  >> 0x00000011U)))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                       ^ ((((QData)((IData)((0x0000007fU 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4)))) 
                            << 0x00000039U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                               >> 7U)) 
                          ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                              << 0x00000017U) | (QData)((IData)(
                                                                (0x007fffffU 
                                                                 & (IData)(
                                                                           (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                                            >> 0x00000029U)))))))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                        ^ ((((QData)((IData)((0x0000007fU 
                                              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4)))) 
                             << 0x00000039U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                >> 7U)) 
                           ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                               << 0x00000017U) | (QData)((IData)(
                                                                 (0x007fffffU 
                                                                  & (IData)(
                                                                            (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                                             >> 0x00000029U)))))))) 
                       >> 0x00000020U));
    }
    if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__kadd_2_done) 
         | (0x0fU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U]);
    }
    if ((9U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (IData)((0x8000000000000000ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
                                                 << 0x00000020U) 
                                                | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U])))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (IData)(((0x8000000000000000ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
                                                  << 0x00000020U) 
                                                 | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U])))) 
                       >> 0x00000020U));
        if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] 
                = (IData)((1ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
                                    << 0x00000020U) 
                                   | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U])))));
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] 
                = (IData)(((1ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
                                     << 0x00000020U) 
                                    | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U])))) 
                           >> 0x00000020U));
        }
    }
    if ((0x0dU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U]);
    }
}

void Vtb_verify___024root___eval_act(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_act\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((0x0000000000000079ULL & vlSelfRef.__VactTriggered[0U])) {
        Vtb_verify___024root___act_comb__TOP__0(vlSelf);
    }
}

void Vtb_verify___024root___nba_sequent__TOP__0(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___nba_sequent__TOP__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __Vdly__tb_verify__DOT__uut__DOT__buf_full;
    __Vdly__tb_verify__DOT__uut__DOT__buf_full = 0;
    CData/*0:0*/ __Vdly__tb_verify__DOT__uut__DOT__tg_beat_idx;
    __Vdly__tb_verify__DOT__uut__DOT__tg_beat_idx = 0;
    // Body
    vlSelfRef.__Vdly__tb_verify__DOT__uut__DOT__rst_sh 
        = vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh;
    __Vdly__tb_verify__DOT__uut__DOT__tg_beat_idx = vlSelfRef.tb_verify__DOT__uut__DOT__tg_beat_idx;
    __Vdly__tb_verify__DOT__uut__DOT__buf_full = vlSelfRef.tb_verify__DOT__uut__DOT__buf_full;
    vlSelfRef.tb_verify__DOT__uut__DOT__msg_win_q = 
        ((IData)(vlSelfRef.tb_verify__DOT__reset_n) 
         && (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window));
    if (vlSelfRef.tb_verify__DOT__reset_n) {
        vlSelfRef.__Vdly__tb_verify__DOT__uut__DOT__rst_sh 
            = (3U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh) 
                     >> 1U));
        if (vlSelfRef.tb_verify__DOT__uut__DOT__launching) {
            vlSelfRef.tb_verify__DOT__uut__DOT__ct_lo = 0ULL;
            vlSelfRef.tb_verify__DOT__uut__DOT__ct_hi = 0ULL;
        }
        if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid) 
             & (3U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type)))) {
            if (vlSelfRef.tb_verify__DOT__uut__DOT__ct_beat_idx) {
                vlSelfRef.tb_verify__DOT__uut__DOT__ct_hi 
                    = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo;
            } else {
                vlSelfRef.tb_verify__DOT__uut__DOT__ct_lo 
                    = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo;
            }
        }
        if (((IData)(vlSelfRef.tb_verify__DOT__valid_data_in) 
             & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[0U] 
                = vlSelfRef.tb_verify__DOT__data_in[0U];
            vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[1U] 
                = vlSelfRef.tb_verify__DOT__data_in[1U];
            vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[2U] 
                = vlSelfRef.tb_verify__DOT__data_in[2U];
            vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[3U] 
                = vlSelfRef.tb_verify__DOT__data_in[3U];
            vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb 
                = vlSelfRef.tb_verify__DOT__valid_bytes;
            vlSelfRef.tb_verify__DOT__uut__DOT__buf_eot 
                = vlSelfRef.tb_verify__DOT__EOT;
            vlSelfRef.tb_verify__DOT__uut__DOT__buf_last 
                = vlSelfRef.tb_verify__DOT__last_block;
            __Vdly__tb_verify__DOT__uut__DOT__buf_full = 1U;
        } else if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__beat_consumed) 
                    & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__last_beat))) {
            __Vdly__tb_verify__DOT__uut__DOT__buf_full = 0U;
        }
        if (vlSelfRef.tb_verify__DOT__uut__DOT__beat_consumed) {
            vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi = 1U;
        } else if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi = 0U;
        }
    } else {
        vlSelfRef.__Vdly__tb_verify__DOT__uut__DOT__rst_sh = 7U;
        vlSelfRef.tb_verify__DOT__uut__DOT__ct_lo = 0ULL;
        vlSelfRef.tb_verify__DOT__uut__DOT__ct_hi = 0ULL;
        __Vdly__tb_verify__DOT__uut__DOT__buf_full = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[0U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[1U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[2U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[3U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__buf_eot = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi = 0U;
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__buf_full = __Vdly__tb_verify__DOT__uut__DOT__buf_full;
    vlSelfRef.tb_verify__DOT__uut__DOT__last_beat = 
        ((8U >= (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb)) 
         | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi));
    if (vlSelfRef.tb_verify__DOT__reset_n) {
        if ((((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_key_valid) 
              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_key_ready)) 
             & (2U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__key_sel = 1U;
        } else if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__key_sel = 0U;
        }
        if (((IData)(vlSelfRef.tb_verify__DOT__load_data) 
             | (IData)(vlSelfRef.tb_verify__DOT__start))) {
            if ((((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_allow) 
                  & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active))) 
                 & (1U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                vlSelfRef.tb_verify__DOT__uut__DOT__run_allow = 0U;
                vlSelfRef.tb_verify__DOT__uut__DOT__run_active = 1U;
                vlSelfRef.tb_verify__DOT__uut__DOT__done_r = 0U;
            }
        } else {
            vlSelfRef.tb_verify__DOT__uut__DOT__run_allow = 1U;
        }
        if ((0x10U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__run_active = 0U;
        }
        if (vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse) {
            vlSelfRef.tb_verify__DOT__uut__DOT__done_r = 1U;
        }
        if ((((3U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready)) 
             & (0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__npub_sel = 1U;
        } else if ((3U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__npub_sel = 0U;
        }
        if (vlSelfRef.tb_verify__DOT__uut__DOT__launching) {
            vlSelfRef.tb_verify__DOT__uut__DOT__ct_beat_idx = 0U;
        }
        if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid) 
             & (3U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__ct_beat_idx = 1U;
        }
    } else {
        vlSelfRef.tb_verify__DOT__uut__DOT__key_sel = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__run_allow = 1U;
        vlSelfRef.tb_verify__DOT__uut__DOT__run_active = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__done_r = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__npub_sel = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__ct_beat_idx = 0U;
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__beat_mask = 
        ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi)
          ? ([&]() {
                vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__v 
                    = ((8U < (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb))
                        ? (0x0000003fU & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb) 
                                          - (IData)(8U)))
                        : 0U);
                vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__Vfuncout 
                    = ((0U == (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__v))
                        ? 0U : ((8U <= (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__v))
                                 ? 0x000000ffU : (0x000000ffU 
                                                  & (((IData)(1U) 
                                                      << 
                                                      (7U 
                                                       & (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__v))) 
                                                     - (IData)(1U)))));
            }(), (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__Vfuncout))
          : ([&]() {
                vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__v 
                    = ((8U <= (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb))
                        ? 8U : (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb));
                vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__Vfuncout 
                    = ((0U == (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__v))
                        ? 0U : ((8U <= (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__v))
                                 ? 0x000000ffU : (0x000000ffU 
                                                  & (((IData)(1U) 
                                                      << 
                                                      (7U 
                                                       & (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__v))) 
                                                     - (IData)(1U)))));
            }(), (IData)(vlSelfRef.__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__Vfuncout)));
    if (vlSelfRef.tb_verify__DOT__reset_n) {
        vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse = 0U;
        if (vlSelfRef.tb_verify__DOT__uut__DOT__launching) {
            vlSelfRef.tb_verify__DOT__uut__DOT__tg1_r = 0ULL;
            vlSelfRef.tb_verify__DOT__uut__DOT__tg2_r = 0ULL;
            __Vdly__tb_verify__DOT__uut__DOT__tg_beat_idx = 0U;
        }
        if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid) 
             & (4U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type)))) {
            if (vlSelfRef.tb_verify__DOT__uut__DOT__tg_beat_idx) {
                vlSelfRef.tb_verify__DOT__uut__DOT__tg2_r 
                    = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo;
                vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse = 1U;
            } else {
                vlSelfRef.tb_verify__DOT__uut__DOT__tg1_r 
                    = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo;
                __Vdly__tb_verify__DOT__uut__DOT__tg_beat_idx = 1U;
            }
        }
    } else {
        __Vdly__tb_verify__DOT__uut__DOT__tg_beat_idx = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__tg1_r = 0ULL;
        vlSelfRef.tb_verify__DOT__uut__DOT__tg2_r = 0ULL;
        vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse = 0U;
    }
    vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__last_beat) 
           & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_eot) 
              | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_last)));
    vlSelfRef.tb_verify__DOT__uut__DOT__tg_beat_idx 
        = __Vdly__tb_verify__DOT__uut__DOT__tg_beat_idx;
}

void Vtb_verify___024root___nba_sequent__TOP__1(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___nba_sequent__TOP__1\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0 = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2 = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4 = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0 = 0;
    // Body
    if ((0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U] = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q = 1U;
    } else {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[0U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[1U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[2U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[3U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[2U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[3U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q 
            = (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d) 
                << 6U) | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d) 
                           << 2U) | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__hash_cnt_d)));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d;
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4 
        = ((((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U]))) 
           ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
               << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U]))));
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0 
        = ((((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U]))) 
           ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
               << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U]))));
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2 
        = ((((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U]))) 
           ^ ((((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
                << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U]))) 
              ^ (QData)((IData)(((0x000000f0U & (((IData)(0x0fU) 
                                                  - 
                                                  ((IData)(0x0cU) 
                                                   - 
                                                   ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                    >> 6U))) 
                                                 << 4U)) 
                                 | (0x0000000fU & ((IData)(0x0cU) 
                                                   - 
                                                   ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                    >> 6U))))))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof 
        = ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
           | ((4U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
              | (5U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec 
        = ((1U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
           | (2U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0 
        = ((4U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | ((8U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
              | ((0x0cU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                 | (0x0eU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))));
    vlSelfRef.tb_verify__DOT__uut__DOT__core_key_ready = 0U;
    if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                  >> 4U)))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                    if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_key_ready = 1U;
                    }
                }
            }
        }
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx = 0U;
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready = 0U;
    vlSelfRef.tb_verify__DOT__uut__DOT__in_ad_window 
        = ((5U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | ((6U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
              | (7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))));
    vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window 
        = ((0x0aU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | (0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
        = (tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4 
           ^ ((~ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0) 
              & (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
                  << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U])))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
        = (tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2 
           ^ ((~ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
                   << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U])))) 
              & tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4));
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0 
        = (tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0 
           ^ ((~ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
                   << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U])))) 
              & tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
           & (4U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))));
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type = 0U;
    if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                    if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx 
                            = (0x0000000fU & ((IData)(3U) 
                                              + ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U)));
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready = 1U;
                    }
                } else {
                    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx 
                        = (0x0000000fU & ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))
                                           ? ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                              >> 2U)
                                           : ((IData)(3U) 
                                              + ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U))));
                }
                if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                              >> 1U)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type 
                        = ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))
                            ? 5U : 4U);
                }
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx 
                    = (0x0000000fU & ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))
                                       ? ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                          >> 2U) : 
                                      ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                       >> 2U)));
                if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready = 1U;
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type 
                        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec)
                            ? 3U : 0U);
                }
            }
        }
    } else if ((4U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx 
                = (0x0000000fU & ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))
                                   ? ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                      >> 2U) : ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                >> 2U)));
            if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready = 1U;
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx 
                = (0x0000000fU & ((IData)(3U) + ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U)));
            vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready = 1U;
        }
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice 
        = ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))
            ? (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q
                                [(((IData)(0x0000003fU) 
                                   + (0x000001ffU & 
                                      VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U))) 
                                  >> 5U)])) << ((0U 
                                                 == 
                                                 (0x0000001fU 
                                                  & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))
                                                 ? 0x00000020U
                                                 : 
                                                ((IData)(0x00000040U) 
                                                 - 
                                                 (0x0000001fU 
                                                  & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U))))) 
               | (((0U == (0x0000001fU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))
                    ? 0ULL : ((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q
                                              [(((IData)(0x0000001fU) 
                                                 + 
                                                 (0x000001ffU 
                                                  & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U))) 
                                                >> 5U)])) 
                              << ((IData)(0x00000020U) 
                                  - (0x0000001fU & 
                                     VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U))))) 
                  | ((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q
                                     [(0x0000000fU 
                                       & (VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U) 
                                          >> 5U))])) 
                     >> (0x0000001fU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))))
            : 0ULL);
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
        = ((((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U]))) 
           ^ (((~ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4) 
               & tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0) 
              ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
        = (tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0 
           ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4);
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
        = ((((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U]))) 
           ^ (((~ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2) 
               & (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
                   << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U])))) 
              ^ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0));
}

void Vtb_verify___024root___nba_sequent__TOP__2(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___nba_sequent__TOP__2\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh = vlSelfRef.__Vdly__tb_verify__DOT__uut__DOT__rst_sh;
    vlSelfRef.tb_verify__DOT__uut__DOT__core_rst = 
        (0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh));
}

void Vtb_verify___024root___nba_comb__TOP__0(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___nba_comb__TOP__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ tb_verify__DOT__uut__DOT__core_bdi_eot;
    tb_verify__DOT__uut__DOT__core_bdi_eot = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__core_bdi_eoi;
    tb_verify__DOT__uut__DOT__core_bdi_eoi = 0;
    CData/*3:0*/ tb_verify__DOT__uut__DOT__core_bdi_type;
    tb_verify__DOT__uut__DOT__core_bdi_type = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__feeding_ad;
    tb_verify__DOT__uut__DOT__feeding_ad = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__feeding_msg;
    tb_verify__DOT__uut__DOT__feeding_msg = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ld_key_done;
    tb_verify__DOT__uut__DOT__u_core__DOT__ld_key_done = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub;
    tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad;
    tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad_done;
    tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad_done = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg_done;
    tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg_done = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash;
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash_done1;
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash_done1 = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag;
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag_done;
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag_done = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5;
    tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5 = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12;
    tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12 = 0;
    CData/*0:0*/ __VdfgRegularize_he50b618e_0_8;
    __VdfgRegularize_he50b618e_0_8 = 0;
    // Body
    vlSelfRef.tb_verify__DOT__uut__DOT__launching = 
        ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active) 
         & (1U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done 
        = ((1U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (0U < ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                     ? 1U : 0U)));
    tb_verify__DOT__uut__DOT__feeding_ad = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full) 
                                            & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_ad_window));
    tb_verify__DOT__uut__DOT__feeding_msg = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full) 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window));
    vlSelfRef.tb_verify__DOT__uut__DOT__core_key_valid 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__launching) 
           | (2U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)));
    vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0 
        = ((IData)(tb_verify__DOT__uut__DOT__feeding_ad) 
           | (IData)(tb_verify__DOT__uut__DOT__feeding_msg));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_key 
        = ((2U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_key_ready) 
              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_key_valid)));
    tb_verify__DOT__uut__DOT__core_bdi_eoi = 0U;
    tb_verify__DOT__uut__DOT__core_bdi_eot = 0U;
    if ((3U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if (vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0) {
            tb_verify__DOT__uut__DOT__core_bdi_eoi 
                = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0) 
                   & (IData)(tb_verify__DOT__uut__DOT__feeding_msg));
            tb_verify__DOT__uut__DOT__core_bdi_eot 
                = vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0;
        }
    }
    tb_verify__DOT__uut__DOT__core_bdi_type = 0U;
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid = 0U;
    if ((3U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        tb_verify__DOT__uut__DOT__core_bdi_type = 1U;
        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid = 0xffU;
    } else if (vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0) {
        tb_verify__DOT__uut__DOT__core_bdi_type = ((IData)(tb_verify__DOT__uut__DOT__feeding_msg)
                                                    ? 3U
                                                    : 2U);
        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid 
            = vlSelfRef.tb_verify__DOT__uut__DOT__beat_mask;
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__ld_key_done 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_key) 
           & (4U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__kadd_2_done 
        = ((5U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
               >> 4U) | (0U < (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag 
        = ((0x12U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((4U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type)) 
              & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready) 
                 & (0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid)))));
    __VdfgRegularize_he50b618e_0_8 = ((0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid)) 
                                      & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready));
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid = 0U;
    if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                              >> 1U)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid = 1U;
                }
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid 
                        = (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
                            & (0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid)))
                            ? 1U : 0U);
                }
            }
        }
    }
    tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12 
        = ((0U < (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid)) 
           & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done 
        = (IData)(((4U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                   & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag)));
    vlSelfRef.tb_verify__DOT__uut__DOT__beat_consumed 
        = ((((IData)(tb_verify__DOT__uut__DOT__feeding_ad) 
             & (2U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type))) 
            | ((IData)(tb_verify__DOT__uut__DOT__feeding_msg) 
               & (3U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type)))) 
           & (IData)(__VdfgRegularize_he50b618e_0_8));
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag 
        = ((0x10U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid));
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash 
        = ((0x11U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg 
        = ((0x0aU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((3U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type)) 
              & ((IData)(__VdfgRegularize_he50b618e_0_8) 
                 & ((~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec)) 
                    | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid)))));
    tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub 
        = ((3U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((1U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type)) 
              & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12)));
    tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad = 
        ((6U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         & ((2U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type)) 
            & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12)));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d 
        = (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 8U));
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d = 0U;
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag_done 
        = (IData)(((4U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                   & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag)));
    tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash_done1 
        = (IData)(((0U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                   & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash)));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done 
        = ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub) 
           & (4U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d 
        = (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 6U));
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d = 0U;
    }
    if (((7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         | ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad) 
            & (0xffU != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid))))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d = 1U;
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         | (((9U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
             & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                >> 4U)) | ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg) 
                           & (0xffU != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid)))))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d = 1U;
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9 
        = ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub) 
           | (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad));
    tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5 
        = (((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad) 
            & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10)) 
           | ((((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad) 
                & (5U == (0x000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) 
               & (0U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))) 
              | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg) 
                  & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10) 
                     | ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof) 
                        & (0U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))))) 
                 | (IData)(tb_verify__DOT__uut__DOT__core_bdi_eot))));
    tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg_done 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg) 
           & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5));
    tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad_done 
        = ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad) 
           & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__hash_cnt_d 
        = (3U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q));
    if ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
        if (tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash_done1) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__hash_cnt_d 
                = (3U & ((IData)(1U) + (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)));
        }
        if (((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad_done) 
             & (IData)(tb_verify__DOT__uut__DOT__core_bdi_eoi))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__hash_cnt_d = 0U;
        }
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_eot_d 
        = (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 7U));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d 
        = (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 4U));
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_eot_d = 0U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d 
            = tb_verify__DOT__uut__DOT__core_bdi_eoi;
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done) {
        if (tb_verify__DOT__uut__DOT__core_bdi_eoi) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d = 1U;
        }
    }
    if (tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad_done) {
        if (tb_verify__DOT__uut__DOT__core_bdi_eot) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_eot_d = 1U;
        }
        if (tb_verify__DOT__uut__DOT__core_bdi_eoi) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d = 1U;
        }
    }
    if (((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg_done) 
         & (IData)(tb_verify__DOT__uut__DOT__core_bdi_eoi))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d = 1U;
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q;
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) {
        if (((1U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                      ? 1U : 0U)) | (2U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                             ? 1U : 0U)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
                = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_key_valid)
                    ? 2U : 3U);
        }
        if ((((3U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                       ? 1U : 0U)) | (4U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                              ? 1U : 0U))) 
             | (5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                        ? 1U : 0U)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 4U;
        }
    }
    if (tb_verify__DOT__uut__DOT__u_core__DOT__ld_key_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 3U;
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 4U;
    }
    if ((IData)(((4U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                 & (0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))))) {
        if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 5U;
        }
        if (((3U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
             | (4U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
                = ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                    ? 0x0bU : 0x0aU);
        }
        if ((5U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 6U;
        }
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__kadd_2_done) {
        if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 9U;
        } else if ((2U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 6U;
        } else if ((3U == (IData)(tb_verify__DOT__uut__DOT__core_bdi_type))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 9U;
        }
    }
    if (tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((0xffU != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid))
                ? 8U : (((1U != (0x0000000fU & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                >> 2U))) 
                         & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec))
                         ? 7U : (((0U != (0x0000000fU 
                                          & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                             >> 2U))) 
                                  & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof))
                                  ? 7U : 8U)));
    }
    if ((7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 8U;
    }
    if ((IData)(((8U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                 & (0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))))) {
        if ((0x00000080U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            if ((0x00000040U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
                if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 9U;
                } else if ((5U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
                        = ((0x00000080U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                            ? ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                                ? 0x0bU : 0x0aU) : 0x0aU);
                }
            } else {
                vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 7U;
            }
        } else {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 6U;
        }
    }
    if ((9U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                ? 0x0dU : 0x0aU);
    }
    if (tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((0xffU != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid))
                ? ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof)
                    ? 0x0eU : 0x0dU) : (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
                                         & (1U != (0x0000000fU 
                                                   & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                      >> 2U))))
                                         ? 0x0bU : 
                                        (((0U != (0x0000000fU 
                                                  & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                     >> 2U))) 
                                          & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof))
                                          ? 0x0bU : 0x0cU)));
    }
    if ((0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof)
                ? 0x0eU : 0x0dU);
    }
    if ((IData)(((0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                 & (0x0cU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))))) {
        if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                          >> 5U)))) {
                vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0bU;
            }
        } else {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0aU;
        }
    }
    if ((0x0dU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0eU;
    }
    if ((IData)(((0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                 & (0x0eU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))
                ? 0x11U : (((4U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
                            | (5U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))))
                            ? 0x11U : 0x0fU));
    }
    if ((0x0fU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((2U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))
                ? 0x12U : 0x10U);
    }
    if (tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash_done1) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0eU;
    }
    if (((3U == (3U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
         & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash_done1))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 1U;
    }
    if (tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 1U;
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d = 1U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 1U;
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d 
        = (0x0000000fU & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                          >> 6U));
    if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d) 
                  >> 4U)))) {
        if ((8U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d))) {
            if ((4U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d))) {
                if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d))) {
                    if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d = 0x0cU;
                    }
                } else if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d 
                        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof)
                            ? 0x0cU : 8U);
                }
            } else if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d) 
                                 >> 1U)))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d 
                        = ((5U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))
                            ? 0x0000000cU : 8U);
                }
            }
        } else if ((4U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d) 
                          >> 1U)))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d = 0x0cU;
                }
            }
        }
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d 
            = (0x0000000fU & (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                               >> 6U) - (IData)(1U)));
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d 
        = (0x0000000fU & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                          >> 2U));
    if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_key) 
         | ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9) 
            | ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg) 
               | ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag) 
                  | ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash) 
                     | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag))))))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d 
            = (0x0000000fU & ((IData)(1U) + ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                             >> 2U)));
    }
    if (((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__ld_key_done) 
         | ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done) 
            | ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__sqz_tag_done) 
               | ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__sqz_hash_done1) 
                  | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done)))))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d = 0U;
    }
    if (((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_ad_done) 
         | (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg_done))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d 
            = (((7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d)) 
                | (0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d)))
                ? (0x0000000fU & ((IData)(1U) + ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U)))
                : 0U);
    }
    if ((7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d = 0U;
    }
    if ((0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d = 0U;
    }
}

void Vtb_verify___024root___nba_comb__TOP__1(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___nba_comb__TOP__1\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_verify__DOT__uut__DOT__core_bdi;
    tb_verify__DOT__uut__DOT__core_bdi = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__auth_d;
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d;
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx;
    tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad;
    tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad = 0;
    // Body
    tb_verify__DOT__uut__DOT__core_bdi = 0ULL;
    if ((3U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        tb_verify__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__npub_sel)
                                               ? vlSelfRef.tb_verify__DOT__nonce2
                                               : vlSelfRef.tb_verify__DOT__nonce1);
    } else if (vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0) {
        tb_verify__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi)
                                               ? (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[3U])) 
                                                   << 0x00000020U) 
                                                  | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[2U])))
                                               : (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[1U])) 
                                                   << 0x00000020U) 
                                                  | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[0U]))));
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[0U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[1U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[2U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d[3U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U];
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_key) {
        VL_ASSIGNSEL_WQ(128, 64, (0x0000007fU & VL_SHIFTL_III(7,32,32, 
                                                              (1U 
                                                               & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                                  >> 2U)), 6U)), vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__key_d, 
                        (((2U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                          & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__key_sel))
                          ? vlSelfRef.tb_verify__DOT__key2
                          : vlSelfRef.tb_verify__DOT__key1));
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0ULL;
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo = 0ULL;
    tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad = 0ULL;
    if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                              >> 1U)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo 
                        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice;
                }
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    if (((1U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
                         | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof))) {
                        vlSelfRef.__Vfunc_pad__8__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_pad__8__in 
                            = tb_verify__DOT__uut__DOT__core_bdi;
                        vlSelf->__Vfunc_pad__8__Vfuncout = 0;
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | (IData)((IData)(((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__8__in))
                                                   : 0U))));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((2U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 8U)))
                                                       : 
                                                      ((1U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((4U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x10U)))
                                                       : 
                                                      ((2U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((8U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x18U)))
                                                       : 
                                                      ((4U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000010U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x20U)))
                                                       : 
                                                      ((8U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000020U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x28U)))
                                                       : 
                                                      ((0x00000010U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000040U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x30U)))
                                                       : 
                                                      ((0x00000020U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_pad__8__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad__8__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000080U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad__8__in 
                                                                  >> 0x38U)))
                                                       : 
                                                      ((0x00000040U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad__8__val))
                                                        ? 1U
                                                        : 0U))))) 
                                  << 0x00000038U));
                        tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad 
                            = vlSelfRef.__Vfunc_pad__8__Vfuncout;
                        tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice 
                               ^ tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad);
                        vlSelfRef.__Vfunc_mask__9__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_mask__9__in1 
                            = tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx;
                        vlSelf->__Vfunc_mask__9__Vfuncout = 0;
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | (IData)((IData)(((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__9__in1))
                                                   : 0U))));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (2U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 8U)))
                                                    : 0U))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (4U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x10U)))
                                                    : 0U))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (8U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x18U)))
                                                    : 0U))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000010U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x20U)))
                                                    : 0U))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000020U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x28U)))
                                                    : 0U))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000040U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x30U)))
                                                    : 0U))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_mask__9__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__9__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000080U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__9__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__9__in1 
                                                               >> 0x38U)))
                                                    : 0U))) 
                                  << 0x00000038U));
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo 
                            = vlSelfRef.__Vfunc_mask__9__Vfuncout;
                    } else if ((2U == (0x0000000fU 
                                       & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
                        vlSelfRef.__Vfunc_pad2__10__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_pad2__10__in2 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice;
                        vlSelfRef.__Vfunc_pad2__10__in1 
                            = tb_verify__DOT__uut__DOT__core_bdi;
                        vlSelf->__Vfunc_pad2__10__Vfuncout = 0;
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | (IData)((IData)((0x000000ffU 
                                                  & ((1U 
                                                      & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                      ? (IData)(vlSelfRef.__Vfunc_pad2__10__in1)
                                                      : (IData)(vlSelfRef.__Vfunc_pad2__10__in2))))));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((2U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 8U)))
                                                       : 
                                                      ((1U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 8U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 8U)))))))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((4U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x10U)))
                                                       : 
                                                      ((2U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x10U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x10U)))))))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((8U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x18U)))
                                                       : 
                                                      ((4U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x18U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x18U)))))))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000010U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x20U)))
                                                       : 
                                                      ((8U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x20U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x20U)))))))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000020U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x28U)))
                                                       : 
                                                      ((0x00000010U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x28U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x28U)))))))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000040U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x30U)))
                                                       : 
                                                      ((0x00000020U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x30U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x30U)))))))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_pad2__10__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_pad2__10__Vfuncout) 
                               | ((QData)((IData)((0x000000ffU 
                                                   & ((0x00000080U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(
                                                                 (vlSelfRef.__Vfunc_pad2__10__in1 
                                                                  >> 0x38U)))
                                                       : 
                                                      ((0x00000040U 
                                                        & (IData)(vlSelfRef.__Vfunc_pad2__10__val))
                                                        ? 
                                                       (1U 
                                                        ^ 
                                                        (0x000000ffU 
                                                         & (IData)(
                                                                   (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                    >> 0x38U))))
                                                        : 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_pad2__10__in2 
                                                                   >> 0x38U)))))))) 
                                  << 0x00000038U));
                        tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad 
                            = vlSelfRef.__Vfunc_pad2__10__Vfuncout;
                        tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                            = tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad;
                        vlSelfRef.__Vfunc_mask__11__val 
                            = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                        vlSelfRef.__Vfunc_mask__11__in1 
                            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice 
                               ^ tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx);
                        vlSelf->__Vfunc_mask__11__Vfuncout = 0;
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffffffffff00ULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | (IData)((IData)(((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(vlSelfRef.__Vfunc_mask__11__in1))
                                                   : 0U))));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffffffff00ffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (2U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 8U)))
                                                    : 0U))) 
                                  << 8U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffffff00ffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (4U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x10U)))
                                                    : 0U))) 
                                  << 0x00000010U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffffff00ffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (8U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x18U)))
                                                    : 0U))) 
                                  << 0x00000018U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffffff00ffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000010U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x20U)))
                                                    : 0U))) 
                                  << 0x00000020U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xffff00ffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000020U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x28U)))
                                                    : 0U))) 
                                  << 0x00000028U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0xff00ffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000040U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x30U)))
                                                    : 0U))) 
                                  << 0x00000030U));
                        vlSelfRef.__Vfunc_mask__11__Vfuncout 
                            = ((0x00ffffffffffffffULL 
                                & vlSelfRef.__Vfunc_mask__11__Vfuncout) 
                               | ((QData)((IData)((
                                                   (0x00000080U 
                                                    & (IData)(vlSelfRef.__Vfunc_mask__11__val))
                                                    ? 
                                                   (0x000000ffU 
                                                    & (IData)(
                                                              (vlSelfRef.__Vfunc_mask__11__in1 
                                                               >> 0x38U)))
                                                    : 0U))) 
                                  << 0x00000038U));
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo 
                            = vlSelfRef.__Vfunc_mask__11__Vfuncout;
                    }
                    if ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
                        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo = 0ULL;
                    }
                }
            }
        }
    } else if ((4U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                vlSelfRef.__Vfunc_pad__12__val = vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid;
                vlSelfRef.__Vfunc_pad__12__in = tb_verify__DOT__uut__DOT__core_bdi;
                vlSelf->__Vfunc_pad__12__Vfuncout = 0;
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffffffffff00ULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | (IData)((IData)(((1U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                           ? (0x000000ffU 
                                              & (IData)(vlSelfRef.__Vfunc_pad__12__in))
                                           : 0U))));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffffffff00ffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((2U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 8U)))
                                               : ((1U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 8U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffffff00ffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((4U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x10U)))
                                               : ((2U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000010U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffffff00ffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((8U & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x18U)))
                                               : ((4U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000018U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffffff00ffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000010U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x20U)))
                                               : ((8U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000020U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xffff00ffffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000020U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x28U)))
                                               : ((0x00000010U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000028U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0xff00ffffffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000040U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x30U)))
                                               : ((0x00000020U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000030U));
                vlSelfRef.__Vfunc_pad__12__Vfuncout 
                    = ((0x00ffffffffffffffULL & vlSelfRef.__Vfunc_pad__12__Vfuncout) 
                       | ((QData)((IData)((0x000000ffU 
                                           & ((0x00000080U 
                                               & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                               ? (0x000000ffU 
                                                  & (IData)(
                                                            (vlSelfRef.__Vfunc_pad__12__in 
                                                             >> 0x38U)))
                                               : ((0x00000040U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__12__val))
                                                   ? 1U
                                                   : 0U))))) 
                          << 0x00000038U));
                tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad 
                    = vlSelfRef.__Vfunc_pad__12__Vfuncout;
                tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                    = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice 
                       ^ tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad);
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                = tb_verify__DOT__uut__DOT__core_bdi;
        }
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 
        (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
               >> 0x0000000aU));
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d 
        = (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 9U));
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 0U;
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d = 0U;
    }
    if (((0x0fU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         & (2U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))))) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d = 1U;
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d 
            = ((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d) 
               & (tb_verify__DOT__uut__DOT__core_bdi 
                  == vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice));
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done) {
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_d 
            = (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                >> 9U) & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d));
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[2U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[3U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U];
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U];
    if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9) 
         | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0 
            = tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx;
        if ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))) {
            VL_ASSIGNSEL_WQ(320, 64, (0x000001ffU & 
                                      VL_SHIFTL_III(9,32,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)), vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d, vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0);
        }
    }
    if (((7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         | (0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1 
            = (1ULL ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice);
        if ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))) {
            VL_ASSIGNSEL_WQ(320, 64, (0x000001ffU & 
                                      VL_SHIFTL_III(9,32,32, (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx), 6U)), vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d, vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1);
        }
    }
    if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) 
         & (((3U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                      ? 1U : 0U)) | (4U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                             ? 1U : 0U))) 
            | (5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                       ? 1U : 0U))))) {
        VL_ASSIGN_W(320, vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d, Vtb_verify__ConstPool__CONST_hab76c978_0);
        if ((1U & (~ VL_ONEHOT_I((((5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                            ? 1U : 0U)) 
                                   << 2U) | (((4U == 
                                               ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                                 ? 1U
                                                 : 0U)) 
                                              << 1U) 
                                             | (3U 
                                                == 
                                                ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                                  ? 1U
                                                  : 0U)))))))) {
            if ((0U != (((5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                  ? 1U : 0U)) << 2U) 
                        | (((4U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                     ? 1U : 0U)) << 1U) 
                           | (3U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                      ? 1U : 0U)))))) {
                if (VL_UNLIKELY((vlSymsp->_vm_contextp__->assertOn()))) {
                    VL_WRITEF_NX("[%0t] %%Error: ascon_core.sv:448: Assertion failed in %Ntb_verify.uut.u_core: unique case, but multiple matches found for '4'h%x'\n",0,
                                 64,VL_TIME_UNITED_Q(1000),
                                 -9,vlSymsp->name(),
                                 4,((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                     ? 1U : 0U));
                    VL_STOP_MT("rtl/ascon_core.sv", 448, "");
                }
            }
        }
        if ((3U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                     ? 1U : 0U))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0002U;
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000801U;
        } else if ((4U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                            ? 1U : 0U))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0003U;
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000800U;
        } else if ((5U == ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                            ? 1U : 0U))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0004U;
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000800U;
        }
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x808c0001U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00001000U;
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[2U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[3U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U];
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U];
    }
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                       ^ ((((QData)((IData)((0x0007ffffU 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                            << 0x0000002dU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                               >> 0x00000013U)) 
                          ^ (((QData)((IData)((0x0fffffffU 
                                               & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                              << 0x00000024U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                 >> 0x0000001cU)))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                        ^ ((((QData)((IData)((0x0007ffffU 
                                              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                             << 0x0000002dU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                >> 0x00000013U)) 
                           ^ (((QData)((IData)((0x0fffffffU 
                                                & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                               << 0x00000024U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                  >> 0x0000001cU)))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[2U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                       ^ (((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                            << 3U) | (QData)((IData)(
                                                     (7U 
                                                      & (IData)(
                                                                (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                 >> 0x0000003dU)))))) 
                          ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                              << 0x00000019U) | (QData)((IData)(
                                                                (0x01ffffffU 
                                                                 & (IData)(
                                                                           (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                            >> 0x00000027U)))))))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[3U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                        ^ (((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                             << 3U) | (QData)((IData)(
                                                      (7U 
                                                       & (IData)(
                                                                 (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                  >> 0x0000003dU)))))) 
                           ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                               << 0x00000019U) | (QData)((IData)(
                                                                 (0x01ffffffU 
                                                                  & (IData)(
                                                                            (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                             >> 0x00000027U)))))))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = (IData)(((~ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2) 
                       ^ ((((QData)((IData)((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                            << 0x0000003fU) | (0x7fffffffffffffffULL 
                                               & (~ 
                                                  (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                   >> 1U)))) 
                          ^ (((QData)((IData)((0x0000003fU 
                                               & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                              << 0x0000003aU) | (0x03ffffffffffffffULL 
                                                 & (~ 
                                                    (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                     >> 6U)))))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = (IData)((((~ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2) 
                        ^ ((((QData)((IData)((1U & 
                                              (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                             << 0x0000003fU) | (0x7fffffffffffffffULL 
                                                & (~ 
                                                   (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                    >> 1U)))) 
                           ^ (((QData)((IData)((0x0000003fU 
                                                & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                               << 0x0000003aU) | (0x03ffffffffffffffULL 
                                                  & (~ 
                                                     (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                      >> 6U)))))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                       ^ ((((QData)((IData)((0x000003ffU 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                            << 0x00000036U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                               >> 0x0000000aU)) 
                          ^ (((QData)((IData)((0x0001ffffU 
                                               & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                              << 0x0000002fU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                 >> 0x00000011U)))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                        ^ ((((QData)((IData)((0x000003ffU 
                                              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                             << 0x00000036U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                >> 0x0000000aU)) 
                           ^ (((QData)((IData)((0x0001ffffU 
                                                & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                               << 0x0000002fU) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                  >> 0x00000011U)))) 
                       >> 0x00000020U));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (IData)((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                       ^ ((((QData)((IData)((0x0000007fU 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4)))) 
                            << 0x00000039U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                               >> 7U)) 
                          ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                              << 0x00000017U) | (QData)((IData)(
                                                                (0x007fffffU 
                                                                 & (IData)(
                                                                           (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                                            >> 0x00000029U)))))))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (IData)(((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                        ^ ((((QData)((IData)((0x0000007fU 
                                              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4)))) 
                             << 0x00000039U) | (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                >> 7U)) 
                           ^ ((vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                               << 0x00000017U) | (QData)((IData)(
                                                                 (0x007fffffU 
                                                                  & (IData)(
                                                                            (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                                             >> 0x00000029U)))))))) 
                       >> 0x00000020U));
    }
    if (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__kadd_2_done) 
         | (0x0fU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U]);
    }
    if ((9U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (IData)((0x8000000000000000ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
                                                 << 0x00000020U) 
                                                | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U])))));
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (IData)(((0x8000000000000000ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
                                                  << 0x00000020U) 
                                                 | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U])))) 
                       >> 0x00000020U));
        if ((0x00000010U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[0U] 
                = (IData)((1ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
                                    << 0x00000020U) 
                                   | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U])))));
            vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[1U] 
                = (IData)(((1ULL ^ (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
                                     << 0x00000020U) 
                                    | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U])))) 
                           >> 0x00000020U));
        }
    }
    if ((0x0dU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U]);
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] 
               ^ vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U]);
    }
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d 
        = ((((((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_d) 
               << 5U) | (((IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d) 
                          << 4U) | ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d) 
                                    << 3U))) | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_eot_d) 
                                                 << 2U) 
                                                | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d) 
                                                    << 1U) 
                                                   | (1U 
                                                      & ((~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done)) 
                                                         & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                                                            >> 5U)))))) 
            << 5U) | (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d) 
                       << 4U) | (0x0000000fU & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done)
                                                 ? 
                                                ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                                                  ? 1U
                                                  : 0U)
                                                 : (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))));
}

void Vtb_verify___024root___eval_nba(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_nba\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_verify___024root___nba_sequent__TOP__0(vlSelf);
    }
    if ((5ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_verify___024root___nba_sequent__TOP__1(vlSelf);
    }
    if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
        vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh 
            = vlSelfRef.__Vdly__tb_verify__DOT__uut__DOT__rst_sh;
        vlSelfRef.tb_verify__DOT__uut__DOT__core_rst 
            = (0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh));
    }
    if ((7ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_verify___024root___nba_comb__TOP__0(vlSelf);
    }
    if ((0x000000000000007fULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_verify___024root___nba_comb__TOP__1(vlSelf);
    }
}

void Vtb_verify___024root___timing_ready(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___timing_ready\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready("@(posedge tb_verify.clk)");
    }
    if ((0x0000000000000010ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_hae8e2579__0.ready("@( (~ tb_verify.uut.buf_full))");
    }
    if ((0x0000000000000020ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h096fd0ca__0.ready("@( ((~ tb_verify.uut.in_msg_window) & tb_verify.uut.msg_win_q))");
    }
    if ((0x0000000000000040ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h8d3cb2b4__0.ready("@( tb_verify.uut.ready_tag_pulse)");
    }
}

void Vtb_verify___024root___timing_resume(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___timing_resume\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_h2e47bcf5__0.moveToResumeQueue(
                                                          "@(posedge tb_verify.clk)");
    vlSelfRef.__VtrigSched_hae8e2579__0.moveToResumeQueue(
                                                          "@( (~ tb_verify.uut.buf_full))");
    vlSelfRef.__VtrigSched_h096fd0ca__0.moveToResumeQueue(
                                                          "@( ((~ tb_verify.uut.in_msg_window) & tb_verify.uut.msg_win_q))");
    vlSelfRef.__VtrigSched_h8d3cb2b4__0.moveToResumeQueue(
                                                          "@( tb_verify.uut.ready_tag_pulse)");
    vlSelfRef.__VtrigSched_h2e47bcf5__0.resume("@(posedge tb_verify.clk)");
    vlSelfRef.__VtrigSched_hae8e2579__0.resume("@( (~ tb_verify.uut.buf_full))");
    vlSelfRef.__VtrigSched_h096fd0ca__0.resume("@( ((~ tb_verify.uut.in_msg_window) & tb_verify.uut.msg_win_q))");
    vlSelfRef.__VtrigSched_h8d3cb2b4__0.resume("@( tb_verify.uut.ready_tag_pulse)");
    if ((8ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_verify___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___trigger_orInto__act_vec_vec\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = (out[n] | in[n]);
        n = ((IData)(1U) + n);
    } while ((0U >= n));
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_verify___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vtb_verify___024root___eval_phase__act(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_phase__act\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    Vtb_verify___024root___eval_triggers_vec__act(vlSelf);
    Vtb_verify___024root___timing_ready(vlSelf);
    Vtb_verify___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_verify___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_verify___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_verify___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_verify___024root___timing_resume(vlSelf);
        Vtb_verify___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtb_verify___024root___eval_phase__inact(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_phase__inact\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("tb_verify.sv", 7, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_verify___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vtb_verify___024root___eval_phase__nba(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_phase__nba\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_verify___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        Vtb_verify___024root___eval_nba(vlSelf);
        Vtb_verify___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_verify___024root___eval(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00000064U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_verify___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("tb_verify.sv", 7, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 100 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00000064U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("tb_verify.sv", 7, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 100 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00000064U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_verify___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("tb_verify.sv", 7, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 100 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_verify___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_verify___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_verify___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root____VbeforeTrig_h2e47bcf5__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((IData)(vlSelfRef.tb_verify__DOT__clk) 
                                  & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__clk__0)))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__clk__0 
        = vlSelfRef.tb_verify__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2e47bcf5__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_verify___024root____VbeforeTrig_hae8e2579__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root____VbeforeTrig_hae8e2579__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    CData/*0:0*/ __Vtrigprevexpr_h36b9350c__0;
    __Vtrigprevexpr_h36b9350c__0 = 0;
    // Body
    __Vtrigprevexpr_h36b9350c__0 = (1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full)));
    __VTmp[0U] = (QData)((IData)((((IData)(__Vtrigprevexpr_h36b9350c__0) 
                                   != (IData)(vlSelfRef.__Vtrigprevexpr_h36b9350c__1)) 
                                  << 4U)));
    vlSelfRef.__Vtrigprevexpr_h36b9350c__1 = __Vtrigprevexpr_h36b9350c__0;
    if ((0x0000000000000010ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_hae8e2579__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_hae8e2579__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_verify___024root____VbeforeTrig_h096fd0ca__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root____VbeforeTrig_h096fd0ca__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    CData/*0:0*/ __Vtrigprevexpr_h9dc7e85d__0;
    __Vtrigprevexpr_h9dc7e85d__0 = 0;
    // Body
    __Vtrigprevexpr_h9dc7e85d__0 = ((~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window)) 
                                    & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__msg_win_q));
    __VTmp[0U] = (QData)((IData)((((IData)(__Vtrigprevexpr_h9dc7e85d__0) 
                                   != (IData)(vlSelfRef.__Vtrigprevexpr_h9dc7e85d__1)) 
                                  << 5U)));
    vlSelfRef.__Vtrigprevexpr_h9dc7e85d__1 = __Vtrigprevexpr_h9dc7e85d__0;
    if ((0x0000000000000020ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h096fd0ca__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_verify___024root____VbeforeTrig_h8d3cb2b4__0(Vtb_verify___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root____VbeforeTrig_h8d3cb2b4__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)((((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse) 
                                   != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__ready_tag_pulse__0)) 
                                  << 6U)));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__ready_tag_pulse__0 
        = vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse;
    if ((0x0000000000000040ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h8d3cb2b4__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_verify___024root___eval_debug_assertions(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_debug_assertions\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG

std::string VL_TO_STRING(const Vtb_verify_tb_verify__DOT__vector_t__struct__0& obj) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root::VL_TO_STRING\n"); );
    // Body
    std::string out;
    out += "'{key1:" + VL_TO_STRING(obj.__PVT__key1);
    out += ", key2:" + VL_TO_STRING(obj.__PVT__key2);
    out += ", nonce1:" + VL_TO_STRING(obj.__PVT__nonce1);
    out += ", nonce2:" + VL_TO_STRING(obj.__PVT__nonce2);
    out += ", exp:" + VL_TO_STRING_W(4, obj.__PVT__exp);
    out += "}";
    return (out);
}
