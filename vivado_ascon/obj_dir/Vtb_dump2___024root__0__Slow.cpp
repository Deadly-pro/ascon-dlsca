// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_dump2.h for the primary calling header

#include "Vtb_dump2__pch.h"

void Vtb_dump2___024root___timing_ready(Vtb_dump2___024root* vlSelf);

VL_ATTR_COLD void Vtb_dump2___024root___eval_static(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_static\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_dump2__DOT__clk = 0U;
    vlSelfRef.tb_dump2__DOT__reset_n = 0U;
    vlSelfRef.tb_dump2__DOT__start = 0U;
    vlSelfRef.tb_dump2__DOT__load_data = 0U;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_dump2__DOT__clk__0 = 0U;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_dump2__DOT__reset_n__0 = 0U;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_dump2__DOT__uut__DOT__core_rst__0 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__core_rst;
    Vtb_dump2___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_dump2___024root___eval_static__TOP(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_static__TOP\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_dump2__DOT__clk = 0U;
    vlSelfRef.tb_dump2__DOT__reset_n = 0U;
    vlSelfRef.tb_dump2__DOT__start = 0U;
    vlSelfRef.tb_dump2__DOT__load_data = 0U;
}

VL_ATTR_COLD void Vtb_dump2___024root___eval_initial__TOP(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_initial__TOP\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_READMEM_N(true, 256, 20, 0, "/tmp/vecs256.hex"s
                 ,  &(vlSelfRef.tb_dump2__DOT__mem)
                 , 0, ~0ULL);
}

VL_ATTR_COLD void Vtb_dump2___024root___eval_final(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_final\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_dump2___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_dump2___024root___eval_phase__stl(Vtb_dump2___024root* vlSelf);

VL_ATTR_COLD void Vtb_dump2___024root___eval_settle(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_settle\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00000064U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_dump2___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("tb_dump2.sv", 2, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 100 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_dump2___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD void Vtb_dump2___024root___eval_triggers_vec__stl(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_triggers_vec__stl\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VstlTriggered[0U] = ((0xfffffffffffffffeULL 
                                      & vlSelfRef.__VstlTriggered[0U]) 
                                     | (IData)((IData)(vlSelfRef.__VstlFirstIteration)));
}

VL_ATTR_COLD bool Vtb_dump2___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_dump2___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_dump2___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_dump2___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___trigger_anySet__stl\n"); );
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

extern const VlWide<10>/*319:0*/ Vtb_dump2__ConstPool__CONST_hab76c978_0;

VL_ATTR_COLD void Vtb_dump2___024root___stl_sequent__TOP__0(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___stl_sequent__TOP__0\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_dump2__DOT__uut__DOT__core_bdi;
    tb_dump2__DOT__uut__DOT__core_bdi = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__core_bdi_eot;
    tb_dump2__DOT__uut__DOT__core_bdi_eot = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__core_bdi_eoi;
    tb_dump2__DOT__uut__DOT__core_bdi_eoi = 0;
    CData/*3:0*/ tb_dump2__DOT__uut__DOT__core_bdi_type;
    tb_dump2__DOT__uut__DOT__core_bdi_type = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__feeding_ad;
    tb_dump2__DOT__uut__DOT__feeding_ad = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__feeding_msg;
    tb_dump2__DOT__uut__DOT__feeding_msg = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__auth_d;
    tb_dump2__DOT__uut__DOT__u_core__DOT__auth_d = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d;
    tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key_done;
    tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key_done = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub;
    tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad;
    tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad_done;
    tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad_done = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg_done;
    tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg_done = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash;
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash_done1;
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash_done1 = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag;
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag_done;
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag_done = 0;
    QData/*63:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx;
    tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0;
    QData/*63:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad;
    tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5;
    tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5 = 0;
    CData/*0:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12;
    tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12 = 0;
    QData/*63:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0;
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0 = 0;
    QData/*63:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2;
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2 = 0;
    QData/*63:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4;
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4 = 0;
    QData/*63:0*/ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0;
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0 = 0;
    CData/*0:0*/ __VdfgRegularize_he50b618e_0_8;
    __VdfgRegularize_he50b618e_0_8 = 0;
    QData/*63:0*/ __Vfunc_mask__3__Vfuncout;
    __Vfunc_mask__3__Vfuncout = 0;
    QData/*63:0*/ __Vfunc_mask__5__Vfuncout;
    __Vfunc_mask__5__Vfuncout = 0;
    // Body
    vlSelfRef.tb_dump2__DOT__uut__DOT__core_rst = (0U 
                                                   != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__rst_sh));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0 
        = ((4U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | ((8U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
              | ((0x0cU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                 | (0x0eU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__core_key_ready = 0U;
    if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                  >> 4U)))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                    if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                        vlSelfRef.tb_dump2__DOT__uut__DOT__core_key_ready = 1U;
                    }
                }
            }
        }
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__launching = 
        ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active) 
         & (1U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)));
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4 
        = ((((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U]))) 
           ^ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
               << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U]))));
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0 
        = ((((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U]))) 
           ^ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
               << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U]))));
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2 
        = ((((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U]))) 
           ^ ((((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
                << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U]))) 
              ^ (QData)((IData)(((0x000000f0U & (((IData)(0x0fU) 
                                                  - 
                                                  ((IData)(0x0cU) 
                                                   - 
                                                   ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                    >> 6U))) 
                                                 << 4U)) 
                                 | (0x0000000fU & ((IData)(0x0cU) 
                                                   - 
                                                   ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                    >> 6U))))))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx = 0U;
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done 
        = ((1U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (0U < ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                     ? 1U : 0U)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__last_beat = 
        ((8U >= (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_vb)) 
         | (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__beat_hi));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof 
        = ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
           | ((4U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
              | (5U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready = 0U;
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec 
        = ((1U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
           | (2U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))));
    if ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                    if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx 
                            = (0x0000000fU & ((IData)(3U) 
                                              + ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U)));
                        vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready = 1U;
                    }
                } else {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx 
                        = (0x0000000fU & ((1U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))
                                           ? ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                              >> 2U)
                                           : ((IData)(3U) 
                                              + ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U))));
                }
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx 
                    = (0x0000000fU & ((1U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))
                                       ? ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                          >> 2U) : 
                                      ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                       >> 2U)));
                if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready = 1U;
                }
            }
        }
    } else if ((4U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx 
                = (0x0000000fU & ((1U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))
                                   ? ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                      >> 2U) : ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                >> 2U)));
            if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready = 1U;
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx 
                = (0x0000000fU & ((IData)(3U) + ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U)));
            vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready = 1U;
        }
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__beat_mask = 
        ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__beat_hi)
          ? ([&]() {
                vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__v 
                    = ((8U < (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_vb))
                        ? (0x0000003fU & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_vb) 
                                          - (IData)(8U)))
                        : 0U);
                vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__Vfuncout 
                    = ((0U == (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__v))
                        ? 0U : ((8U <= (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__v))
                                 ? 0x000000ffU : (0x000000ffU 
                                                  & (((IData)(1U) 
                                                      << 
                                                      (7U 
                                                       & (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__v))) 
                                                     - (IData)(1U)))));
            }(), (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__Vfuncout))
          : ([&]() {
                vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__v 
                    = ((8U <= (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_vb))
                        ? 8U : (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_vb));
                vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__Vfuncout 
                    = ((0U == (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__v))
                        ? 0U : ((8U <= (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__v))
                                 ? 0x000000ffU : (0x000000ffU 
                                                  & (((IData)(1U) 
                                                      << 
                                                      (7U 
                                                       & (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__v))) 
                                                     - (IData)(1U)))));
            }(), (IData)(vlSelfRef.__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__Vfuncout)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__in_ad_window 
        = ((5U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | ((6U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
              | (7U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__in_msg_window 
        = ((0x0aU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | (0x0bU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__core_key_valid 
        = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__launching) 
           | (2U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
        = (tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4 
           ^ ((~ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0) 
              & (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
                  << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U])))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
        = (tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2 
           ^ ((~ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
                   << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U])))) 
              & tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4));
    tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0 
        = (tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0 
           ^ ((~ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
                   << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U])))) 
              & tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice 
        = ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))
            ? (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q
                                [(((IData)(0x0000003fU) 
                                   + (0x000001ffU & 
                                      VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U))) 
                                  >> 5U)])) << ((0U 
                                                 == 
                                                 (0x0000001fU 
                                                  & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))
                                                 ? 0x00000020U
                                                 : 
                                                ((IData)(0x00000040U) 
                                                 - 
                                                 (0x0000001fU 
                                                  & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U))))) 
               | (((0U == (0x0000001fU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))
                    ? 0ULL : ((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q
                                              [(((IData)(0x0000001fU) 
                                                 + 
                                                 (0x000001ffU 
                                                  & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U))) 
                                                >> 5U)])) 
                              << ((IData)(0x00000020U) 
                                  - (0x0000001fU & 
                                     VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U))))) 
                  | ((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q
                                     [(0x0000000fU 
                                       & (VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U) 
                                          >> 5U))])) 
                     >> (0x0000001fU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))))
            : 0ULL);
    vlSelfRef.tb_dump2__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0 
        = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__last_beat) 
           & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_eot) 
              | (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_last)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_type = 0U;
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10 
        = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
           & (4U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))));
    tb_dump2__DOT__uut__DOT__feeding_ad = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_full) 
                                           & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__in_ad_window));
    tb_dump2__DOT__uut__DOT__feeding_msg = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_full) 
                                            & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__in_msg_window));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key 
        = ((2U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_key_ready) 
              & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_key_valid)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
        = ((((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U]))) 
           ^ (((~ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4) 
               & tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0) 
              ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
        = (tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0 
           ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4);
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
        = ((((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U])) 
             << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U]))) 
           ^ (((~ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2) 
               & (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U])) 
                   << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U])))) 
              ^ tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0));
    vlSelfRef.tb_dump2__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0 
        = ((IData)(tb_dump2__DOT__uut__DOT__feeding_ad) 
           | (IData)(tb_dump2__DOT__uut__DOT__feeding_msg));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__key_d[0U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__key_d[1U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__key_d[2U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__key_d[3U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U];
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key) {
        VL_ASSIGNSEL_WQ(128, 64, (0x0000007fU & VL_SHIFTL_III(7,32,32, 
                                                              (1U 
                                                               & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                                  >> 2U)), 6U)), vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__key_d, 
                        (((2U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                          & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__key_sel))
                          ? vlSelfRef.tb_dump2__DOT__key2
                          : vlSelfRef.tb_dump2__DOT__key1));
        tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key_done 
            = (4U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)));
    } else {
        tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key_done = 0U;
    }
    tb_dump2__DOT__uut__DOT__core_bdi_eoi = 0U;
    tb_dump2__DOT__uut__DOT__core_bdi = 0ULL;
    tb_dump2__DOT__uut__DOT__core_bdi_eot = 0U;
    if ((3U != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if (vlSelfRef.tb_dump2__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0) {
            tb_dump2__DOT__uut__DOT__core_bdi_eoi = 
                ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0) 
                 & (IData)(tb_dump2__DOT__uut__DOT__feeding_msg));
            tb_dump2__DOT__uut__DOT__core_bdi_eot = vlSelfRef.tb_dump2__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0;
        }
    }
    tb_dump2__DOT__uut__DOT__core_bdi_type = 0U;
    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid = 0U;
    if ((3U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        tb_dump2__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__npub_sel)
                                              ? vlSelfRef.tb_dump2__DOT__nonce2
                                              : vlSelfRef.tb_dump2__DOT__nonce1);
        tb_dump2__DOT__uut__DOT__core_bdi_type = 1U;
        vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid = 0xffU;
    } else if (vlSelfRef.tb_dump2__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0) {
        tb_dump2__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__beat_hi)
                                              ? (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_data[3U])) 
                                                  << 0x00000020U) 
                                                 | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_data[2U])))
                                              : (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_data[1U])) 
                                                  << 0x00000020U) 
                                                 | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__buf_data[0U]))));
        tb_dump2__DOT__uut__DOT__core_bdi_type = ((IData)(tb_dump2__DOT__uut__DOT__feeding_msg)
                                                   ? 3U
                                                   : 2U);
        vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid 
            = vlSelfRef.tb_dump2__DOT__uut__DOT__beat_mask;
    }
    tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0ULL;
    tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad = 0ULL;
    if ((! (1U & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                  >> 4U)))) {
        if ((8U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                    if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                        if (((1U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
                             | (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof))) {
                            vlSelfRef.__Vfunc_pad__2__val 
                                = vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid;
                            vlSelfRef.__Vfunc_pad__2__in 
                                = tb_dump2__DOT__uut__DOT__core_bdi;
                            vlSelf->__Vfunc_pad__2__Vfuncout = 0;
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0xffffffffffffff00ULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | (IData)((IData)(
                                                     ((1U 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(vlSelfRef.__Vfunc_pad__2__in))
                                                       : 0U))));
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0xffffffffffff00ffULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((2U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad__2__in 
                                                                      >> 8U)))
                                                           : 
                                                          ((1U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                            ? 1U
                                                            : 0U))))) 
                                      << 8U));
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0xffffffffff00ffffULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((4U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad__2__in 
                                                                      >> 0x10U)))
                                                           : 
                                                          ((2U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                            ? 1U
                                                            : 0U))))) 
                                      << 0x00000010U));
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0xffffffff00ffffffULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((8U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad__2__in 
                                                                      >> 0x18U)))
                                                           : 
                                                          ((4U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                            ? 1U
                                                            : 0U))))) 
                                      << 0x00000018U));
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0xffffff00ffffffffULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000010U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad__2__in 
                                                                      >> 0x20U)))
                                                           : 
                                                          ((8U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                            ? 1U
                                                            : 0U))))) 
                                      << 0x00000020U));
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0xffff00ffffffffffULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000020U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad__2__in 
                                                                      >> 0x28U)))
                                                           : 
                                                          ((0x00000010U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                            ? 1U
                                                            : 0U))))) 
                                      << 0x00000028U));
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0xff00ffffffffffffULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000040U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad__2__in 
                                                                      >> 0x30U)))
                                                           : 
                                                          ((0x00000020U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                            ? 1U
                                                            : 0U))))) 
                                      << 0x00000030U));
                            vlSelfRef.__Vfunc_pad__2__Vfuncout 
                                = ((0x00ffffffffffffffULL 
                                    & vlSelfRef.__Vfunc_pad__2__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000080U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad__2__in 
                                                                      >> 0x38U)))
                                                           : 
                                                          ((0x00000040U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad__2__val))
                                                            ? 1U
                                                            : 0U))))) 
                                      << 0x00000038U));
                            tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad 
                                = vlSelfRef.__Vfunc_pad__2__Vfuncout;
                            tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                                = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice 
                                   ^ tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad);
                            vlSelfRef.__Vfunc_mask__3__val 
                                = vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid;
                            vlSelfRef.__Vfunc_mask__3__in1 
                                = tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx;
                            __Vfunc_mask__3__Vfuncout = 0;
                            __Vfunc_mask__3__Vfuncout 
                                = ((0xffffffffffffff00ULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | (IData)((IData)(
                                                     ((1U 
                                                       & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(vlSelfRef.__Vfunc_mask__3__in1))
                                                       : 0U))));
                            __Vfunc_mask__3__Vfuncout 
                                = ((0xffffffffffff00ffULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((2U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__3__in1 
                                                                   >> 8U)))
                                                        : 0U))) 
                                      << 8U));
                            __Vfunc_mask__3__Vfuncout 
                                = ((0xffffffffff00ffffULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((4U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__3__in1 
                                                                   >> 0x10U)))
                                                        : 0U))) 
                                      << 0x00000010U));
                            __Vfunc_mask__3__Vfuncout 
                                = ((0xffffffff00ffffffULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((8U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__3__in1 
                                                                   >> 0x18U)))
                                                        : 0U))) 
                                      << 0x00000018U));
                            __Vfunc_mask__3__Vfuncout 
                                = ((0xffffff00ffffffffULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000010U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__3__in1 
                                                                   >> 0x20U)))
                                                        : 0U))) 
                                      << 0x00000020U));
                            __Vfunc_mask__3__Vfuncout 
                                = ((0xffff00ffffffffffULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000020U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__3__in1 
                                                                   >> 0x28U)))
                                                        : 0U))) 
                                      << 0x00000028U));
                            __Vfunc_mask__3__Vfuncout 
                                = ((0xff00ffffffffffffULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000040U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__3__in1 
                                                                   >> 0x30U)))
                                                        : 0U))) 
                                      << 0x00000030U));
                            __Vfunc_mask__3__Vfuncout 
                                = ((0x00ffffffffffffffULL 
                                    & __Vfunc_mask__3__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000080U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__3__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__3__in1 
                                                                   >> 0x38U)))
                                                        : 0U))) 
                                      << 0x00000038U));
                        } else if ((2U == (0x0000000fU 
                                           & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
                            vlSelfRef.__Vfunc_pad2__4__val 
                                = vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid;
                            vlSelfRef.__Vfunc_pad2__4__in2 
                                = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice;
                            vlSelfRef.__Vfunc_pad2__4__in1 
                                = tb_dump2__DOT__uut__DOT__core_bdi;
                            vlSelf->__Vfunc_pad2__4__Vfuncout = 0;
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0xffffffffffffff00ULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | (IData)((IData)(
                                                     (0x000000ffU 
                                                      & ((1U 
                                                          & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                          ? (IData)(vlSelfRef.__Vfunc_pad2__4__in1)
                                                          : (IData)(vlSelfRef.__Vfunc_pad2__4__in2))))));
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0xffffffffffff00ffULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((2U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad2__4__in1 
                                                                      >> 8U)))
                                                           : 
                                                          ((1U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                            ? 
                                                           (1U 
                                                            ^ 
                                                            (0x000000ffU 
                                                             & (IData)(
                                                                       (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                        >> 8U))))
                                                            : 
                                                           (0x000000ffU 
                                                            & (IData)(
                                                                      (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                       >> 8U)))))))) 
                                      << 8U));
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0xffffffffff00ffffULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((4U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad2__4__in1 
                                                                      >> 0x10U)))
                                                           : 
                                                          ((2U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                            ? 
                                                           (1U 
                                                            ^ 
                                                            (0x000000ffU 
                                                             & (IData)(
                                                                       (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                        >> 0x10U))))
                                                            : 
                                                           (0x000000ffU 
                                                            & (IData)(
                                                                      (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                       >> 0x10U)))))))) 
                                      << 0x00000010U));
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0xffffffff00ffffffULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((8U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad2__4__in1 
                                                                      >> 0x18U)))
                                                           : 
                                                          ((4U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                            ? 
                                                           (1U 
                                                            ^ 
                                                            (0x000000ffU 
                                                             & (IData)(
                                                                       (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                        >> 0x18U))))
                                                            : 
                                                           (0x000000ffU 
                                                            & (IData)(
                                                                      (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                       >> 0x18U)))))))) 
                                      << 0x00000018U));
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0xffffff00ffffffffULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000010U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad2__4__in1 
                                                                      >> 0x20U)))
                                                           : 
                                                          ((8U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                            ? 
                                                           (1U 
                                                            ^ 
                                                            (0x000000ffU 
                                                             & (IData)(
                                                                       (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                        >> 0x20U))))
                                                            : 
                                                           (0x000000ffU 
                                                            & (IData)(
                                                                      (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                       >> 0x20U)))))))) 
                                      << 0x00000020U));
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0xffff00ffffffffffULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000020U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad2__4__in1 
                                                                      >> 0x28U)))
                                                           : 
                                                          ((0x00000010U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                            ? 
                                                           (1U 
                                                            ^ 
                                                            (0x000000ffU 
                                                             & (IData)(
                                                                       (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                        >> 0x28U))))
                                                            : 
                                                           (0x000000ffU 
                                                            & (IData)(
                                                                      (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                       >> 0x28U)))))))) 
                                      << 0x00000028U));
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0xff00ffffffffffffULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000040U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad2__4__in1 
                                                                      >> 0x30U)))
                                                           : 
                                                          ((0x00000020U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                            ? 
                                                           (1U 
                                                            ^ 
                                                            (0x000000ffU 
                                                             & (IData)(
                                                                       (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                        >> 0x30U))))
                                                            : 
                                                           (0x000000ffU 
                                                            & (IData)(
                                                                      (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                       >> 0x30U)))))))) 
                                      << 0x00000030U));
                            vlSelfRef.__Vfunc_pad2__4__Vfuncout 
                                = ((0x00ffffffffffffffULL 
                                    & vlSelfRef.__Vfunc_pad2__4__Vfuncout) 
                                   | ((QData)((IData)(
                                                      (0x000000ffU 
                                                       & ((0x00000080U 
                                                           & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                           ? 
                                                          (0x000000ffU 
                                                           & (IData)(
                                                                     (vlSelfRef.__Vfunc_pad2__4__in1 
                                                                      >> 0x38U)))
                                                           : 
                                                          ((0x00000040U 
                                                            & (IData)(vlSelfRef.__Vfunc_pad2__4__val))
                                                            ? 
                                                           (1U 
                                                            ^ 
                                                            (0x000000ffU 
                                                             & (IData)(
                                                                       (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                        >> 0x38U))))
                                                            : 
                                                           (0x000000ffU 
                                                            & (IData)(
                                                                      (vlSelfRef.__Vfunc_pad2__4__in2 
                                                                       >> 0x38U)))))))) 
                                      << 0x00000038U));
                            tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad 
                                = vlSelfRef.__Vfunc_pad2__4__Vfuncout;
                            tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                                = tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad;
                            vlSelfRef.__Vfunc_mask__5__val 
                                = vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid;
                            vlSelfRef.__Vfunc_mask__5__in1 
                                = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice 
                                   ^ tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx);
                            __Vfunc_mask__5__Vfuncout = 0;
                            __Vfunc_mask__5__Vfuncout 
                                = ((0xffffffffffffff00ULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | (IData)((IData)(
                                                     ((1U 
                                                       & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                       ? 
                                                      (0x000000ffU 
                                                       & (IData)(vlSelfRef.__Vfunc_mask__5__in1))
                                                       : 0U))));
                            __Vfunc_mask__5__Vfuncout 
                                = ((0xffffffffffff00ffULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((2U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__5__in1 
                                                                   >> 8U)))
                                                        : 0U))) 
                                      << 8U));
                            __Vfunc_mask__5__Vfuncout 
                                = ((0xffffffffff00ffffULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((4U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__5__in1 
                                                                   >> 0x10U)))
                                                        : 0U))) 
                                      << 0x00000010U));
                            __Vfunc_mask__5__Vfuncout 
                                = ((0xffffffff00ffffffULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((8U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__5__in1 
                                                                   >> 0x18U)))
                                                        : 0U))) 
                                      << 0x00000018U));
                            __Vfunc_mask__5__Vfuncout 
                                = ((0xffffff00ffffffffULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000010U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__5__in1 
                                                                   >> 0x20U)))
                                                        : 0U))) 
                                      << 0x00000020U));
                            __Vfunc_mask__5__Vfuncout 
                                = ((0xffff00ffffffffffULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000020U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__5__in1 
                                                                   >> 0x28U)))
                                                        : 0U))) 
                                      << 0x00000028U));
                            __Vfunc_mask__5__Vfuncout 
                                = ((0xff00ffffffffffffULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000040U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__5__in1 
                                                                   >> 0x30U)))
                                                        : 0U))) 
                                      << 0x00000030U));
                            __Vfunc_mask__5__Vfuncout 
                                = ((0x00ffffffffffffffULL 
                                    & __Vfunc_mask__5__Vfuncout) 
                                   | ((QData)((IData)(
                                                      ((0x00000080U 
                                                        & (IData)(vlSelfRef.__Vfunc_mask__5__val))
                                                        ? 
                                                       (0x000000ffU 
                                                        & (IData)(
                                                                  (vlSelfRef.__Vfunc_mask__5__in1 
                                                                   >> 0x38U)))
                                                        : 0U))) 
                                      << 0x00000038U));
                        }
                    }
                }
            }
        } else if ((4U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    vlSelfRef.__Vfunc_pad__6__val = vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid;
                    vlSelfRef.__Vfunc_pad__6__in = tb_dump2__DOT__uut__DOT__core_bdi;
                    vlSelf->__Vfunc_pad__6__Vfuncout = 0;
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0xffffffffffffff00ULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | (IData)((IData)(((1U & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                               ? (0x000000ffU 
                                                  & (IData)(vlSelfRef.__Vfunc_pad__6__in))
                                               : 0U))));
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0xffffffffffff00ffULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | ((QData)((IData)((0x000000ffU 
                                               & ((2U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(
                                                             (vlSelfRef.__Vfunc_pad__6__in 
                                                              >> 8U)))
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                    ? 1U
                                                    : 0U))))) 
                              << 8U));
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0xffffffffff00ffffULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | ((QData)((IData)((0x000000ffU 
                                               & ((4U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(
                                                             (vlSelfRef.__Vfunc_pad__6__in 
                                                              >> 0x10U)))
                                                   : 
                                                  ((2U 
                                                    & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                    ? 1U
                                                    : 0U))))) 
                              << 0x00000010U));
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0xffffffff00ffffffULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | ((QData)((IData)((0x000000ffU 
                                               & ((8U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(
                                                             (vlSelfRef.__Vfunc_pad__6__in 
                                                              >> 0x18U)))
                                                   : 
                                                  ((4U 
                                                    & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                    ? 1U
                                                    : 0U))))) 
                              << 0x00000018U));
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0xffffff00ffffffffULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | ((QData)((IData)((0x000000ffU 
                                               & ((0x00000010U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(
                                                             (vlSelfRef.__Vfunc_pad__6__in 
                                                              >> 0x20U)))
                                                   : 
                                                  ((8U 
                                                    & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                    ? 1U
                                                    : 0U))))) 
                              << 0x00000020U));
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0xffff00ffffffffffULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | ((QData)((IData)((0x000000ffU 
                                               & ((0x00000020U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(
                                                             (vlSelfRef.__Vfunc_pad__6__in 
                                                              >> 0x28U)))
                                                   : 
                                                  ((0x00000010U 
                                                    & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                    ? 1U
                                                    : 0U))))) 
                              << 0x00000028U));
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0xff00ffffffffffffULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | ((QData)((IData)((0x000000ffU 
                                               & ((0x00000040U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(
                                                             (vlSelfRef.__Vfunc_pad__6__in 
                                                              >> 0x30U)))
                                                   : 
                                                  ((0x00000020U 
                                                    & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                    ? 1U
                                                    : 0U))))) 
                              << 0x00000030U));
                    vlSelfRef.__Vfunc_pad__6__Vfuncout 
                        = ((0x00ffffffffffffffULL & vlSelfRef.__Vfunc_pad__6__Vfuncout) 
                           | ((QData)((IData)((0x000000ffU 
                                               & ((0x00000080U 
                                                   & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                   ? 
                                                  (0x000000ffU 
                                                   & (IData)(
                                                             (vlSelfRef.__Vfunc_pad__6__in 
                                                              >> 0x38U)))
                                                   : 
                                                  ((0x00000040U 
                                                    & (IData)(vlSelfRef.__Vfunc_pad__6__val))
                                                    ? 1U
                                                    : 0U))))) 
                              << 0x00000038U));
                    tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad 
                        = vlSelfRef.__Vfunc_pad__6__Vfuncout;
                    tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                        = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice 
                           ^ tb_dump2__DOT__uut__DOT__u_core__DOT__bdi_pad);
                }
            }
        } else if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
            if ((1U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx 
                    = tb_dump2__DOT__uut__DOT__core_bdi;
            }
        }
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__kadd_2_done 
        = ((5U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
               >> 4U) | (0U < (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag 
        = ((0x12U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((4U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type)) 
              & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready) 
                 & (0U != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid)))));
    __VdfgRegularize_he50b618e_0_8 = ((0U != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid)) 
                                      & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready));
    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_valid = 0U;
    if ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                              >> 1U)))) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_type 
                        = ((1U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))
                            ? 5U : 4U);
                    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_valid = 1U;
                }
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_type 
                        = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec)
                            ? 3U : 0U);
                    vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_valid 
                        = (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
                            & (0U != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid)))
                            ? 1U : 0U);
                }
            }
        }
    }
    tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12 
        = ((0U < (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid)) 
           & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_ready));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag_done 
        = (IData)(((4U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                   & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__beat_consumed 
        = ((((IData)(tb_dump2__DOT__uut__DOT__feeding_ad) 
             & (2U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type))) 
            | ((IData)(tb_dump2__DOT__uut__DOT__feeding_msg) 
               & (3U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type)))) 
           & (IData)(__VdfgRegularize_he50b618e_0_8));
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag = 
        ((0x10U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_valid));
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash 
        = ((0x11U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_valid));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg 
        = ((0x0aU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((3U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type)) 
              & ((IData)(__VdfgRegularize_he50b618e_0_8) 
                 & ((~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec)) 
                    | (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdo_valid)))));
    tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub = 
        ((3U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         & ((1U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type)) 
            & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12)));
    tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad = 
        ((6U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         & ((2U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type)) 
            & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__auth_valid_d 
        = (1U & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 8U));
    tb_dump2__DOT__uut__DOT__u_core__DOT__auth_d = 
        (1U & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
               >> 0x0000000aU));
    tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d 
        = (1U & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 9U));
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__auth_valid_d = 0U;
        tb_dump2__DOT__uut__DOT__u_core__DOT__auth_d = 0U;
        tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d = 0U;
    }
    if (((0x0fU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         & (2U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))))) {
        tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d = 1U;
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag) {
        tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d 
            = ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d) 
               & (tb_dump2__DOT__uut__DOT__core_bdi 
                  == vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice));
    }
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag_done 
        = (IData)(((4U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                   & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag)));
    tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash_done1 
        = (IData)(((0U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                   & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash)));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub_done 
        = ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub) 
           & (4U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_pad_d 
        = (1U & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 6U));
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_pad_d = 0U;
    }
    if (((7U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         | ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad) 
            & (0xffU != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid))))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_pad_d = 1U;
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         | (((9U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
             & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                >> 4U)) | ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg) 
                           & (0xffU != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid)))))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_pad_d = 1U;
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9 
        = ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub) 
           | (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad));
    tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5 
        = (((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad) 
            & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10)) 
           | ((((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad) 
                & (5U == (0x000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) 
               & (0U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))) 
              | (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg) 
                  & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10) 
                     | ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof) 
                        & (0U == (0x003cU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))))) 
                 | (IData)(tb_dump2__DOT__uut__DOT__core_bdi_eot))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[0U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[1U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[2U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[2U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[3U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[3U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[4U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[5U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[6U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[7U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[8U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U];
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[9U] 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U];
    if (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9) 
         | (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0 
            = tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice_nx;
        if ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))) {
            VL_ASSIGNSEL_WQ(320, 64, (0x000001ffU & 
                                      VL_SHIFTL_III(9,32,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)), vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d, vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0);
        }
    }
    if (((7U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
         | (0x0bU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1 
            = (1ULL ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice);
        if ((0x013fU >= (0x000001ffU & VL_SHIFTL_III(9,9,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)))) {
            VL_ASSIGNSEL_WQ(320, 64, (0x000001ffU & 
                                      VL_SHIFTL_III(9,32,32, (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx), 6U)), vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d, vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1);
        }
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__auth_valid_d = 1U;
        tb_dump2__DOT__uut__DOT__u_core__DOT__auth_d 
            = (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                >> 9U) & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d));
    }
    if (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done) 
         & (((3U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                      ? 1U : 0U)) | (4U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                             ? 1U : 0U))) 
            | (5U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                       ? 1U : 0U))))) {
        VL_ASSIGN_W(320, vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d, Vtb_dump2__ConstPool__CONST_hab76c978_0);
        if ((1U & (~ VL_ONEHOT_I((((5U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                            ? 1U : 0U)) 
                                   << 2U) | (((4U == 
                                               ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                                 ? 1U
                                                 : 0U)) 
                                              << 1U) 
                                             | (3U 
                                                == 
                                                ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                                  ? 1U
                                                  : 0U)))))))) {
            if ((0U != (((5U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                  ? 1U : 0U)) << 2U) 
                        | (((4U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                     ? 1U : 0U)) << 1U) 
                           | (3U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                      ? 1U : 0U)))))) {
                if (VL_UNLIKELY((vlSymsp->_vm_contextp__->assertOn()))) {
                    VL_WRITEF_NX("[%0t] %%Error: ascon_core.sv:385: Assertion failed in %Ntb_dump2.uut.u_core: unique case, but multiple matches found for '4'h%x'\n",0,
                                 64,VL_TIME_UNITED_Q(1000),
                                 -9,vlSymsp->name(),
                                 4,((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                     ? 1U : 0U));
                    VL_STOP_MT("rtl/ascon_core.sv", 385, "");
                }
            }
        }
        if ((3U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                     ? 1U : 0U))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0002U;
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000801U;
        } else if ((4U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                            ? 1U : 0U))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0003U;
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000800U;
        } else if ((5U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                            ? 1U : 0U))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x00cc0004U;
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00000800U;
        }
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[0U] = 0x808c0001U;
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[1U] = 0x00001000U;
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[2U] 
            = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U];
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[3U] 
            = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U];
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U];
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U];
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[0U] 
            = (IData)((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                       ^ ((((QData)((IData)((0x0007ffffU 
                                             & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                            << 0x0000002dU) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                               >> 0x00000013U)) 
                          ^ (((QData)((IData)((0x0fffffffU 
                                               & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                              << 0x00000024U) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                 >> 0x0000001cU)))));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[1U] 
            = (IData)(((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                        ^ ((((QData)((IData)((0x0007ffffU 
                                              & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                             << 0x0000002dU) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                >> 0x00000013U)) 
                           ^ (((QData)((IData)((0x0fffffffU 
                                                & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0)))) 
                               << 0x00000024U) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 
                                                  >> 0x0000001cU)))) 
                       >> 0x00000020U));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[2U] 
            = (IData)((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                       ^ (((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                            << 3U) | (QData)((IData)(
                                                     (7U 
                                                      & (IData)(
                                                                (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                 >> 0x0000003dU)))))) 
                          ^ ((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                              << 0x00000019U) | (QData)((IData)(
                                                                (0x01ffffffU 
                                                                 & (IData)(
                                                                           (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                            >> 0x00000027U)))))))));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[3U] 
            = (IData)(((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                        ^ (((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                             << 3U) | (QData)((IData)(
                                                      (7U 
                                                       & (IData)(
                                                                 (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                  >> 0x0000003dU)))))) 
                           ^ ((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                               << 0x00000019U) | (QData)((IData)(
                                                                 (0x01ffffffU 
                                                                  & (IData)(
                                                                            (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 
                                                                             >> 0x00000027U)))))))) 
                       >> 0x00000020U));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = (IData)(((~ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2) 
                       ^ ((((QData)((IData)((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                            << 0x0000003fU) | (0x7fffffffffffffffULL 
                                               & (~ 
                                                  (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                   >> 1U)))) 
                          ^ (((QData)((IData)((0x0000003fU 
                                               & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                              << 0x0000003aU) | (0x03ffffffffffffffULL 
                                                 & (~ 
                                                    (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                     >> 6U)))))));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = (IData)((((~ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2) 
                        ^ ((((QData)((IData)((1U & 
                                              (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                             << 0x0000003fU) | (0x7fffffffffffffffULL 
                                                & (~ 
                                                   (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                    >> 1U)))) 
                           ^ (((QData)((IData)((0x0000003fU 
                                                & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2))))) 
                               << 0x0000003aU) | (0x03ffffffffffffffULL 
                                                  & (~ 
                                                     (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 
                                                      >> 6U)))))) 
                       >> 0x00000020U));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (IData)((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                       ^ ((((QData)((IData)((0x000003ffU 
                                             & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                            << 0x00000036U) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                               >> 0x0000000aU)) 
                          ^ (((QData)((IData)((0x0001ffffU 
                                               & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                              << 0x0000002fU) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                 >> 0x00000011U)))));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (IData)(((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                        ^ ((((QData)((IData)((0x000003ffU 
                                              & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                             << 0x00000036U) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                >> 0x0000000aU)) 
                           ^ (((QData)((IData)((0x0001ffffU 
                                                & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3)))) 
                               << 0x0000002fU) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 
                                                  >> 0x00000011U)))) 
                       >> 0x00000020U));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (IData)((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                       ^ ((((QData)((IData)((0x0000007fU 
                                             & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4)))) 
                            << 0x00000039U) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                               >> 7U)) 
                          ^ ((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                              << 0x00000017U) | (QData)((IData)(
                                                                (0x007fffffU 
                                                                 & (IData)(
                                                                           (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                                            >> 0x00000029U)))))))));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (IData)(((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                        ^ ((((QData)((IData)((0x0000007fU 
                                              & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4)))) 
                             << 0x00000039U) | (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                >> 7U)) 
                           ^ ((vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                               << 0x00000017U) | (QData)((IData)(
                                                                 (0x007fffffU 
                                                                  & (IData)(
                                                                            (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 
                                                                             >> 0x00000029U)))))))) 
                       >> 0x00000020U));
    }
    if (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__kadd_2_done) 
         | (0x0fU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U]);
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U]);
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U]);
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U]);
    }
    if ((9U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[8U] 
            = (IData)((0x8000000000000000ULL ^ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
                                                 << 0x00000020U) 
                                                | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U])))));
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[9U] 
            = (IData)(((0x8000000000000000ULL ^ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[9U])) 
                                                  << 0x00000020U) 
                                                 | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[8U])))) 
                       >> 0x00000020U));
        if ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[0U] 
                = (IData)((1ULL ^ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
                                    << 0x00000020U) 
                                   | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U])))));
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[1U] 
                = (IData)(((1ULL ^ (((QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[1U])) 
                                     << 0x00000020U) 
                                    | (QData)((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[0U])))) 
                           >> 0x00000020U));
        }
    }
    tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg_done 
        = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg) 
           & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5));
    tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad_done 
        = ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad) 
           & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__hash_cnt_d 
        = (3U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q));
    if ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
        if (tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash_done1) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__hash_cnt_d 
                = (3U & ((IData)(1U) + (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)));
        }
        if (((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad_done) 
             & (IData)(tb_dump2__DOT__uut__DOT__core_bdi_eoi))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__hash_cnt_d = 0U;
        }
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_eot_d 
        = (1U & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 7U));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__eoi_d 
        = (1U & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 4U));
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_eot_d = 0U;
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__eoi_d 
            = tb_dump2__DOT__uut__DOT__core_bdi_eoi;
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub_done) {
        if (tb_dump2__DOT__uut__DOT__core_bdi_eoi) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__eoi_d = 1U;
        }
    }
    if (tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad_done) {
        if (tb_dump2__DOT__uut__DOT__core_bdi_eot) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_eot_d = 1U;
        }
        if (tb_dump2__DOT__uut__DOT__core_bdi_eoi) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__eoi_d = 1U;
        }
    }
    if (((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg_done) 
         & (IData)(tb_dump2__DOT__uut__DOT__core_bdi_eoi))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__eoi_d = 1U;
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
        = vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q;
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done) {
        if (((1U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                      ? 1U : 0U)) | (2U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                             ? 1U : 0U)))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
                = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_key_valid)
                    ? 2U : 3U);
        }
        if ((((3U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                       ? 1U : 0U)) | (4U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                              ? 1U : 0U))) 
             | (5U == ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                        ? 1U : 0U)))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 4U;
        }
    }
    if (tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 3U;
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 4U;
    }
    if ((IData)(((4U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                 & (0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))))) {
        if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 5U;
        }
        if (((3U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
             | (4U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
                = ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                    ? 0x0bU : 0x0aU);
        }
        if ((5U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 6U;
        }
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__kadd_2_done) {
        if ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 9U;
        } else if ((2U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 6U;
        } else if ((3U == (IData)(tb_dump2__DOT__uut__DOT__core_bdi_type))) {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 9U;
        }
    }
    if (tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((0xffU != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid))
                ? 8U : (((1U != (0x0000000fU & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                >> 2U))) 
                         & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec))
                         ? 7U : (((0U != (0x0000000fU 
                                          & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                             >> 2U))) 
                                  & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof))
                                  ? 7U : 8U)));
    }
    if ((7U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 8U;
    }
    if ((IData)(((8U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q)) 
                 & (0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)))))) {
        if ((0x00000080U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            if ((0x00000040U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
                if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 9U;
                } else if ((5U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
                        = ((0x00000080U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                            ? ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                                ? 0x0bU : 0x0aU) : 0x0aU);
                }
            } else {
                vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 7U;
            }
        } else {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 6U;
        }
    }
    if ((9U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))
                ? 0x0dU : 0x0aU);
    }
    if (tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((0xffU != (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__core_bdi_valid))
                ? ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof)
                    ? 0x0eU : 0x0dU) : (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
                                         & (1U != (0x0000000fU 
                                                   & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                      >> 2U))))
                                         ? 0x0bU : 
                                        (((0U != (0x0000000fU 
                                                  & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                     >> 2U))) 
                                          & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof))
                                          ? 0x0bU : 0x0cU)));
    }
    if ((0x0bU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof)
                ? 0x0eU : 0x0dU);
    }
    if ((IData)(((0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                 & (0x0cU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))))) {
        if ((0x00000010U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                          >> 5U)))) {
                vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0bU;
            }
        } else {
            vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0aU;
        }
    }
    if ((0x0dU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[4U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[4U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[0U]);
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[5U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[5U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[1U]);
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[6U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[6U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[2U]);
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__state_d[7U] 
            = (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q[7U] 
               ^ vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q[3U]);
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0eU;
    }
    if ((IData)(((0x0040U == (0x03c0U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
                 & (0x0eU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))
                ? 0x11U : (((4U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
                            | (5U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))))
                            ? 0x11U : 0x0fU));
    }
    if ((0x0fU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d 
            = ((2U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))
                ? 0x12U : 0x10U);
    }
    if (tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash_done1) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 0x0eU;
    }
    if (((3U == (3U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))) 
         & (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash_done1))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 1U;
    }
    if (tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 1U;
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag_done) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = 1U;
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d 
        = ((((((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__auth_d) 
               << 5U) | (((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__auth_intern_d) 
                          << 4U) | ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__auth_valid_d) 
                                    << 3U))) | (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_eot_d) 
                                                 << 2U) 
                                                | (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ad_pad_d) 
                                                    << 1U) 
                                                   | (1U 
                                                      & ((~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done)) 
                                                         & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                                                            >> 5U)))))) 
            << 5U) | (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__eoi_d) 
                       << 4U) | (0x0000000fU & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done)
                                                 ? 
                                                ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__run_active)
                                                  ? 1U
                                                  : 0U)
                                                 : (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))));
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__round_cnt_d 
        = (0x0000000fU & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                          >> 6U));
    if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d) 
                  >> 4U)))) {
        if ((8U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d))) {
            if ((4U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d))) {
                if ((2U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d))) {
                    if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__round_cnt_d = 0x0cU;
                    }
                } else if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__round_cnt_d 
                        = ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof)
                            ? 0x0cU : 8U);
                }
            } else if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d) 
                                 >> 1U)))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__round_cnt_d 
                        = ((5U == (0x0000000fU & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))
                            ? 0x0000000cU : 8U);
                }
            }
        } else if ((4U & (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d))) {
            if ((1U & (~ ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d) 
                          >> 1U)))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d)))) {
                    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__round_cnt_d = 0x0cU;
                }
            }
        }
    }
    if (vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__round_cnt_d 
            = (0x0000000fU & (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                               >> 6U) - (IData)(1U)));
    }
    vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__word_cnt_d 
        = (0x0000000fU & ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                          >> 2U));
    if (((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key) 
         | ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9) 
            | ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg) 
               | ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag) 
                  | ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash) 
                     | (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag))))))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__word_cnt_d 
            = (0x0000000fU & ((IData)(1U) + ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                             >> 2U)));
    }
    if (((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key_done) 
         | ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub_done) 
            | ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_tag_done) 
               | ((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__sqz_hash_done1) 
                  | (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag_done)))))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__word_cnt_d = 0U;
    }
    if (((IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_ad_done) 
         | (IData)(tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg_done))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__word_cnt_d 
            = (((7U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d)) 
                | (0x0bU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d)))
                ? (0x0000000fU & ((IData)(1U) + ((IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q) 
                                                 >> 2U)))
                : 0U);
    }
    if ((7U == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__word_cnt_d = 0U;
    }
    if ((0x0bU == (IData)(vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        vlSelfRef.tb_dump2__DOT__uut__DOT__u_core__DOT__word_cnt_d = 0U;
    }
}

VL_ATTR_COLD void Vtb_dump2___024root___eval_stl(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_stl\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
        Vtb_dump2___024root___stl_sequent__TOP__0(vlSelf);
    }
}

VL_ATTR_COLD bool Vtb_dump2___024root___eval_phase__stl(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___eval_phase__stl\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VstlExecute;
    // Body
    Vtb_dump2___024root___eval_triggers_vec__stl(vlSelf);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_dump2___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_dump2___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        Vtb_dump2___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

bool Vtb_dump2___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_dump2___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_dump2___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_dump2.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge tb_dump2.reset_n)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @(posedge tb_dump2.uut.core_rst)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 3U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 3 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_dump2___024root___ctor_var_reset(Vtb_dump2___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_dump2___024root___ctor_var_reset\n"); );
    Vtb_dump2__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_dump2__DOT__key1 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12054453433934765258ull);
    vlSelf->tb_dump2__DOT__key2 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6119245374006308008ull);
    vlSelf->tb_dump2__DOT__nonce1 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12365702005029913409ull);
    vlSelf->tb_dump2__DOT__nonce2 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17163896630688830888ull);
    vlSelf->tb_dump2__DOT__cyc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15559096581052582762ull);
    for (int __Vi0 = 0; __Vi0 < 20; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(256, vlSelf->tb_dump2__DOT__mem[__Vi0], __VscopeHash, 4120513670755837704ull);
    }
    vlSelf->tb_dump2__DOT__uut__DOT__rst_sh = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 364617154240225792ull);
    vlSelf->tb_dump2__DOT__uut__DOT__core_rst = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4814115640600686206ull);
    vlSelf->tb_dump2__DOT__uut__DOT__core_key_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17928055431778203301ull);
    vlSelf->tb_dump2__DOT__uut__DOT__core_key_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7992236452973853289ull);
    vlSelf->tb_dump2__DOT__uut__DOT__core_bdi_valid = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6451077370618486863ull);
    vlSelf->tb_dump2__DOT__uut__DOT__core_bdi_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 650512612639917727ull);
    vlSelf->tb_dump2__DOT__uut__DOT__core_bdo_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18020585376761934577ull);
    vlSelf->tb_dump2__DOT__uut__DOT__core_bdo_type = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 7082284843951657953ull);
    vlSelf->tb_dump2__DOT__uut__DOT__in_ad_window = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4057928301238929509ull);
    vlSelf->tb_dump2__DOT__uut__DOT__in_msg_window = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4558164737353337647ull);
    vlSelf->tb_dump2__DOT__uut__DOT__run_allow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6148608989338641543ull);
    vlSelf->tb_dump2__DOT__uut__DOT__run_active = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3027520173856221165ull);
    vlSelf->tb_dump2__DOT__uut__DOT__launching = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15841241856533982843ull);
    vlSelf->tb_dump2__DOT__uut__DOT__key_sel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4770804248345270445ull);
    vlSelf->tb_dump2__DOT__uut__DOT__npub_sel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9575425482230032963ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_dump2__DOT__uut__DOT__buf_data, __VscopeHash, 9805290267841971837ull);
    vlSelf->tb_dump2__DOT__uut__DOT__buf_vb = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 2887422521011613114ull);
    vlSelf->tb_dump2__DOT__uut__DOT__buf_eot = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10629997010131395493ull);
    vlSelf->tb_dump2__DOT__uut__DOT__buf_last = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11021500746810191180ull);
    vlSelf->tb_dump2__DOT__uut__DOT__buf_full = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2435845274573719604ull);
    vlSelf->tb_dump2__DOT__uut__DOT__beat_hi = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1338656164185312611ull);
    vlSelf->tb_dump2__DOT__uut__DOT__last_beat = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8044482339141089780ull);
    vlSelf->tb_dump2__DOT__uut__DOT__beat_mask = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3036736903447500160ull);
    vlSelf->tb_dump2__DOT__uut__DOT__beat_consumed = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18128147386772322857ull);
    vlSelf->tb_dump2__DOT__uut__DOT__tg_beat_idx = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3244856368074661727ull);
    vlSelf->tb_dump2__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0 = 0;
    vlSelf->tb_dump2__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0 = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1 = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0 = 0;
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__key_d, __VscopeHash, 4634912280153401729ull);
    VL_SCOPED_RAND_RESET_W(320, vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__state_d, __VscopeHash, 1144163090010720153ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__round_cnt_d = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 18196998912328862519ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__word_cnt_d = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1158268250677301853ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__hash_cnt_d = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 2398693520394311018ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_d = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 6206728081105052123ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__fsm_q = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 5245498719653669985ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__auth_valid_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13934796071441259161ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__ad_eot_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9938859012346945896ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__ad_pad_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2269892743915574591ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__eoi_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18001980017209408182ull);
    VL_ZERO_RESET_W(128, vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q);
    VL_ZERO_RESET_W(320, vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__mode_enc_dec = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9354364482570501723ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__mode_hash_xof = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15843902758283893764ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__idle_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17957911372231614192ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__ld_key = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3563087142389235796ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__ld_npub_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15749561454060604602ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__kadd_2_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13708823288167996485ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__abs_msg = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2046595269047353475ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14280035539944902916ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__ver_tag_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16329218543613336212ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__state_idx = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1842542947253575916ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__state_slice = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 63638854654128984ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0 = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9 = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10 = 0;
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15788445796744958590ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6450749033275806542ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 16045600317182752169ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 525561041437838127ull);
    vlSelf->tb_dump2__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6260510708799479777ull);
    vlSelf->__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__Vfuncout = 0;
    vlSelf->__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__0__v = 0;
    vlSelf->__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__Vfuncout = 0;
    vlSelf->__Vfunc_tb_dump2__DOT__uut__DOT__vb_mask__1__v = 0;
    vlSelf->__Vfunc_pad__2__Vfuncout = 0;
    vlSelf->__Vfunc_pad__2__in = 0;
    vlSelf->__Vfunc_pad__2__val = 0;
    vlSelf->__Vfunc_mask__3__in1 = 0;
    vlSelf->__Vfunc_mask__3__val = 0;
    vlSelf->__Vfunc_pad2__4__Vfuncout = 0;
    vlSelf->__Vfunc_pad2__4__in1 = 0;
    vlSelf->__Vfunc_pad2__4__in2 = 0;
    vlSelf->__Vfunc_pad2__4__val = 0;
    vlSelf->__Vfunc_mask__5__in1 = 0;
    vlSelf->__Vfunc_mask__5__val = 0;
    vlSelf->__Vfunc_pad__6__Vfuncout = 0;
    vlSelf->__Vfunc_pad__6__in = 0;
    vlSelf->__Vfunc_pad__6__val = 0;
    vlSelf->__Vdly__tb_dump2__DOT__uut__DOT__rst_sh = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_dump2__DOT__clk__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__tb_dump2__DOT__reset_n__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__tb_dump2__DOT__uut__DOT__core_rst__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
