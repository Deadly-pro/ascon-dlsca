// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_verify.h for the primary calling header

#include "Vtb_verify__pch.h"

VL_ATTR_COLD void Vtb_verify___024root___eval_static__TOP(Vtb_verify___024root* vlSelf);
void Vtb_verify___024root___timing_ready(Vtb_verify___024root* vlSelf);

VL_ATTR_COLD void Vtb_verify___024root___eval_static(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_static\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_verify___024root___eval_static__TOP(vlSelf);
    vlSelfRef.__VactTriggered[0U] = (0x0000000000000010ULL 
                                     | vlSelfRef.__VactTriggered[0U]);
    vlSelfRef.__VactTriggered[0U] = (0x0000000000000020ULL 
                                     | vlSelfRef.__VactTriggered[0U]);
    vlSelfRef.__VactTriggered[0U] = (0x0000000000000040ULL 
                                     | vlSelfRef.__VactTriggered[0U]);
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__clk__0 = 0U;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__reset_n__0 = 0U;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__core_rst__0 
        = vlSelfRef.tb_verify__DOT__uut__DOT__core_rst;
    vlSelfRef.__Vtrigprevexpr_h36b9350c__1 = (1U & 
                                              (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full)));
    vlSelfRef.__Vtrigprevexpr_h9dc7e85d__1 = ((~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window)) 
                                              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__msg_win_q));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__ready_tag_pulse__0 
        = vlSelfRef.tb_verify__DOT__uut__DOT__ready_tag_pulse;
    Vtb_verify___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_verify___024root___eval_static__TOP(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_static__TOP\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<4>/*127:0*/ __Vtemp_2;
    VlWide<4>/*127:0*/ __Vtemp_3;
    VlWide<4>/*127:0*/ __Vtemp_4;
    VlWide<4>/*127:0*/ __Vtemp_5;
    // Body
    vlSelfRef.tb_verify__DOT__clk = 0U;
    vlSelfRef.tb_verify__DOT__reset_n = 0U;
    vlSelfRef.tb_verify__DOT__start = 0U;
    vlSelfRef.tb_verify__DOT__load_data = 0U;
    vlSelfRef.tb_verify__DOT__data_in[0U] = 0U;
    vlSelfRef.tb_verify__DOT__data_in[1U] = 0U;
    vlSelfRef.tb_verify__DOT__data_in[2U] = 0U;
    vlSelfRef.tb_verify__DOT__data_in[3U] = 0U;
    vlSelfRef.tb_verify__DOT__valid_data_in = 0U;
    vlSelfRef.tb_verify__DOT__last_block = 0U;
    vlSelfRef.tb_verify__DOT__valid_bytes = 0U;
    vlSelfRef.tb_verify__DOT__EOT = 0U;
    __Vtemp_1[0U] = 0x19378c6aU;
    __Vtemp_1[1U] = 0xcaa719a7U;
    __Vtemp_1[2U] = 0x6b6a4fe5U;
    __Vtemp_1[3U] = 0x19c8f96aU;
    vlSelfRef.tb_verify__DOT__vectors[0U] = Vtb_verify_tb_verify__DOT__vector_t__struct__0{
        .__PVT__key1 = 0x0706050403020100ULL, .__PVT__key2 = 0x0f0e0d0c0b0a0908ULL, 
        .__PVT__nonce1 = 0x0706050403020100ULL, .__PVT__nonce2 = 0x0f0e0d0c0b0a0908ULL, 
        .__PVT__exp = __Vtemp_1};
    __Vtemp_2[0U] = 0xd1dc9341U;
    __Vtemp_2[1U] = 0x5c828fe6U;
    __Vtemp_2[2U] = 0x9fa87308U;
    __Vtemp_2[3U] = 0x94f0b9bcU;
    vlSelfRef.tb_verify__DOT__vectors[1U] = Vtb_verify_tb_verify__DOT__vector_t__struct__0{
        .__PVT__key1 = 0xbebafecaefbeaddeULL, .__PVT__key2 = 0x0706050403020100ULL, 
        .__PVT__nonce1 = 0x8070605040302010ULL, .__PVT__nonce2 = 0x00f0e0d0c0b0a090ULL, 
        .__PVT__exp = __Vtemp_2};
    __Vtemp_3[0U] = 0x9761cfb5U;
    __Vtemp_3[1U] = 0x053815e8U;
    __Vtemp_3[2U] = 0x8ec81e2eU;
    __Vtemp_3[3U] = 0x3e2a5669U;
    vlSelfRef.tb_verify__DOT__vectors[2U] = Vtb_verify_tb_verify__DOT__vector_t__struct__0{
        .__PVT__key1 = 0ULL, .__PVT__key2 = 0ULL, .__PVT__nonce1 = 0ULL, 
        .__PVT__nonce2 = 0ULL, .__PVT__exp = __Vtemp_3};
    __Vtemp_4[0U] = 0x864ebb5aU;
    __Vtemp_4[1U] = 0x9bf43620U;
    __Vtemp_4[2U] = 0xd41bbe29U;
    __Vtemp_4[3U] = 0x6a9d3f7aU;
    vlSelfRef.tb_verify__DOT__vectors[3U] = Vtb_verify_tb_verify__DOT__vector_t__struct__0{
        .__PVT__key1 = 0xffffffffffffffffULL, .__PVT__key2 = 0xffffffffffffffffULL, 
        .__PVT__nonce1 = 0xffffffffffffffffULL, .__PVT__nonce2 = 0xffffffffffffffffULL, 
        .__PVT__exp = __Vtemp_4};
    __Vtemp_5[0U] = 0x4dc496f3U;
    __Vtemp_5[1U] = 0xc9d47072U;
    __Vtemp_5[2U] = 0x6152408dU;
    __Vtemp_5[3U] = 0x50207437U;
    vlSelfRef.tb_verify__DOT__vectors[4U] = Vtb_verify_tb_verify__DOT__vector_t__struct__0{
        .__PVT__key1 = 0xefcdab8967452301ULL, .__PVT__key2 = 0xefcdab8967452301ULL, 
        .__PVT__nonce1 = 0x1032547698badcfeULL, .__PVT__nonce2 = 0x1032547698badcfeULL, 
        .__PVT__exp = __Vtemp_5};
}

VL_ATTR_COLD void Vtb_verify___024root___eval_final(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_final\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_verify___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_verify___024root___eval_phase__stl(Vtb_verify___024root* vlSelf);

VL_ATTR_COLD void Vtb_verify___024root___eval_settle(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_settle\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00000064U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_verify___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("tb_verify.sv", 7, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 100 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_verify___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD void Vtb_verify___024root___eval_triggers_vec__stl(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_triggers_vec__stl\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VstlTriggered[0U] = ((0xfffffffffffffffeULL 
                                      & vlSelfRef.__VstlTriggered[0U]) 
                                     | (IData)((IData)(vlSelfRef.__VstlFirstIteration)));
}

VL_ATTR_COLD bool Vtb_verify___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_verify___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_verify___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_verify___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___trigger_anySet__stl\n"); );
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

VL_ATTR_COLD void Vtb_verify___024root___stl_sequent__TOP__0(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___stl_sequent__TOP__0\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_verify__DOT__uut__DOT__core_bdi;
    tb_verify__DOT__uut__DOT__core_bdi = 0;
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
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__auth_d;
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d;
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d = 0;
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
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx;
    tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad;
    tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5;
    tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_5 = 0;
    CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12;
    tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_12 = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a0 = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a2 = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__a4 = 0;
    QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0;
    tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b0 = 0;
    CData/*0:0*/ __VdfgRegularize_he50b618e_0_8;
    __VdfgRegularize_he50b618e_0_8 = 0;
    // Body
    vlSelfRef.tb_verify__DOT__uut__DOT__core_rst = 
        (0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__rst_sh));
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
    vlSelfRef.tb_verify__DOT__uut__DOT__launching = 
        ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active) 
         & (1U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)));
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
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_idx = 0U;
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done 
        = ((1U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & (0U < ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__run_active)
                     ? 1U : 0U)));
    vlSelfRef.tb_verify__DOT__uut__DOT__last_beat = 
        ((8U >= (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_vb)) 
         | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof 
        = ((3U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
           | ((4U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
              | (5U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q)))));
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_ready = 0U;
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec 
        = ((1U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))) 
           | (2U == (0x0000000fU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q))));
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
    vlSelfRef.tb_verify__DOT__uut__DOT__in_ad_window 
        = ((5U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | ((6U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
              | (7U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))));
    vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window 
        = ((0x0aU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           | (0x0bU == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)));
    vlSelfRef.tb_verify__DOT__uut__DOT__core_key_valid 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__launching) 
           | (2U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)));
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
    vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__last_beat) 
           & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_eot) 
              | (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_last)));
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type = 0U;
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10 
        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
           & (4U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q))));
    tb_verify__DOT__uut__DOT__feeding_ad = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full) 
                                            & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_ad_window));
    tb_verify__DOT__uut__DOT__feeding_msg = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_full) 
                                             & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__in_msg_window));
    vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ld_key 
        = ((2U == (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)) 
           & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_key_ready) 
              & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_key_valid)));
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
    vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0 
        = ((IData)(tb_verify__DOT__uut__DOT__feeding_ad) 
           | (IData)(tb_verify__DOT__uut__DOT__feeding_msg));
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
        tb_verify__DOT__uut__DOT__u_core__DOT__ld_key_done 
            = (4U == (0x003cU & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q)));
    } else {
        tb_verify__DOT__uut__DOT__u_core__DOT__ld_key_done = 0U;
    }
    tb_verify__DOT__uut__DOT__core_bdi_eoi = 0U;
    tb_verify__DOT__uut__DOT__core_bdi = 0ULL;
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
        tb_verify__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__npub_sel)
                                               ? vlSelfRef.tb_verify__DOT__nonce2
                                               : vlSelfRef.tb_verify__DOT__nonce1);
        tb_verify__DOT__uut__DOT__core_bdi_type = 1U;
        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid = 0xffU;
    } else if (vlSelfRef.tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0) {
        tb_verify__DOT__uut__DOT__core_bdi = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__beat_hi)
                                               ? (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[3U])) 
                                                   << 0x00000020U) 
                                                  | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[2U])))
                                               : (((QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[1U])) 
                                                   << 0x00000020U) 
                                                  | (QData)((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__buf_data[0U]))));
        tb_verify__DOT__uut__DOT__core_bdi_type = ((IData)(tb_verify__DOT__uut__DOT__feeding_msg)
                                                    ? 3U
                                                    : 2U);
        vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid 
            = vlSelfRef.tb_verify__DOT__uut__DOT__beat_mask;
    }
    tb_verify__DOT__uut__DOT__u_core__DOT__state_slice_nx = 0ULL;
    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo = 0ULL;
    tb_verify__DOT__uut__DOT__u_core__DOT__bdi_pad = 0ULL;
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
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type 
                        = ((1U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))
                            ? 5U : 4U);
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo 
                        = vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__state_slice;
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid = 1U;
                }
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q)))) {
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_type 
                        = ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec)
                            ? 3U : 0U);
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
                    vlSelfRef.tb_verify__DOT__uut__DOT__core_bdo_valid 
                        = (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec) 
                            & (0U != (IData)(vlSelfRef.tb_verify__DOT__uut__DOT__core_bdi_valid)))
                            ? 1U : 0U);
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
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_d = 
        (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
               >> 0x0000000aU));
    tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d 
        = (1U & ((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                 >> 9U));
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__idle_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d = 0U;
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
    if (vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done) {
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d = 1U;
        tb_verify__DOT__uut__DOT__u_core__DOT__auth_d 
            = (((IData)(vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q) 
                >> 9U) & (IData)(tb_verify__DOT__uut__DOT__u_core__DOT__auth_intern_d));
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
        vlSelfRef.tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = 1U;
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

VL_ATTR_COLD void Vtb_verify___024root___eval_stl(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_stl\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
        Vtb_verify___024root___stl_sequent__TOP__0(vlSelf);
    }
}

VL_ATTR_COLD bool Vtb_verify___024root___eval_phase__stl(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___eval_phase__stl\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VstlExecute;
    // Body
    Vtb_verify___024root___eval_triggers_vec__stl(vlSelf);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_verify___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_verify___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        Vtb_verify___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

bool Vtb_verify___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_verify___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_verify___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_verify.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge tb_verify.reset_n)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @(posedge tb_verify.uut.core_rst)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 3U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 3 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
    if ((1U & (IData)((triggers[0U] >> 4U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 4 is active: @( (~ tb_verify.uut.buf_full))\n");
    }
    if ((1U & (IData)((triggers[0U] >> 5U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 5 is active: @( ((~ tb_verify.uut.in_msg_window) & tb_verify.uut.msg_win_q))\n");
    }
    if ((1U & (IData)((triggers[0U] >> 6U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 6 is active: @( tb_verify.uut.ready_tag_pulse)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_verify___024root___ctor_var_reset(Vtb_verify___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_verify___024root___ctor_var_reset\n"); );
    Vtb_verify__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_verify__DOT__key1 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2048570011765850394ull);
    vlSelf->tb_verify__DOT__key2 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13301017311067954423ull);
    vlSelf->tb_verify__DOT__nonce1 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10484556824863312957ull);
    vlSelf->tb_verify__DOT__nonce2 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7360704991240982058ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_verify__DOT__exp_ro, __VscopeHash, 8539227697189899078ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_verify__DOT__simulated_ro, __VscopeHash, 6316360665900990869ull);
    vlSelf->tb_verify__DOT__done_flag = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9745870233321453550ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_verify__DOT__latched_ct, __VscopeHash, 7566590629347233133ull);
    vlSelf->tb_verify__DOT__latched_tag1 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9420415770768413342ull);
    vlSelf->tb_verify__DOT__latched_tag2 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1313646776462305714ull);
    vlSelf->tb_verify__DOT__uut__DOT__rst_sh = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16618258942115966501ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_rst = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10444545198886206941ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_key_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13336582652463405589ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_key_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8958505356402483963ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_bdi_valid = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8961470022598270161ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_bdi_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16969975437484637877ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_bdo = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5300738822784467592ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_bdo_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2403688356331298926ull);
    vlSelf->tb_verify__DOT__uut__DOT__core_bdo_type = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8073318037598200196ull);
    vlSelf->tb_verify__DOT__uut__DOT__in_ad_window = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5928661553339533555ull);
    vlSelf->tb_verify__DOT__uut__DOT__in_msg_window = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 587462574151901453ull);
    vlSelf->tb_verify__DOT__uut__DOT__run_allow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6603685741376179928ull);
    vlSelf->tb_verify__DOT__uut__DOT__run_active = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16178350844938370596ull);
    vlSelf->tb_verify__DOT__uut__DOT__done_r = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6246468220840423033ull);
    vlSelf->tb_verify__DOT__uut__DOT__launching = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11697332397798055937ull);
    vlSelf->tb_verify__DOT__uut__DOT__key_sel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9973356459008629842ull);
    vlSelf->tb_verify__DOT__uut__DOT__npub_sel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15201702524556594913ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_verify__DOT__uut__DOT__buf_data, __VscopeHash, 1202052760854822501ull);
    vlSelf->tb_verify__DOT__uut__DOT__buf_vb = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 11326540347189575357ull);
    vlSelf->tb_verify__DOT__uut__DOT__buf_eot = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7443094633484594027ull);
    vlSelf->tb_verify__DOT__uut__DOT__buf_last = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12294611169227120391ull);
    vlSelf->tb_verify__DOT__uut__DOT__buf_full = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9864537496641335865ull);
    vlSelf->tb_verify__DOT__uut__DOT__beat_hi = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5144328969405005987ull);
    vlSelf->tb_verify__DOT__uut__DOT__last_beat = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4641301972998915068ull);
    vlSelf->tb_verify__DOT__uut__DOT__beat_mask = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13804240184594191224ull);
    vlSelf->tb_verify__DOT__uut__DOT__beat_consumed = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7215775368424138042ull);
    vlSelf->tb_verify__DOT__uut__DOT__msg_win_q = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11620757174162812304ull);
    vlSelf->tb_verify__DOT__uut__DOT__ct_lo = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5579438466151654662ull);
    vlSelf->tb_verify__DOT__uut__DOT__ct_hi = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 101169302559117562ull);
    vlSelf->tb_verify__DOT__uut__DOT__tg1_r = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12172615814616391276ull);
    vlSelf->tb_verify__DOT__uut__DOT__tg2_r = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4972717263993337220ull);
    vlSelf->tb_verify__DOT__uut__DOT__ct_beat_idx = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15808363593944436331ull);
    vlSelf->tb_verify__DOT__uut__DOT__tg_beat_idx = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7987061719041467278ull);
    vlSelf->tb_verify__DOT__uut__DOT__ready_tag_pulse = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1463997690190560434ull);
    vlSelf->tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0 = 0;
    vlSelf->tb_verify__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0 = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1 = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0 = 0;
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__key_d, __VscopeHash, 13197618991878341061ull);
    VL_SCOPED_RAND_RESET_W(320, vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__state_d, __VscopeHash, 16066556323582835024ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 12090539478151372128ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1105545918265374501ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__hash_cnt_d = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 17934056581035883111ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 8982844214937441534ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 6108655646493155058ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5719405560558514438ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__ad_eot_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16558801335058901710ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5578669889780845236ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12311568062786724311ull);
    VL_ZERO_RESET_W(128, vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q);
    VL_ZERO_RESET_W(320, vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 732518620079189387ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10857429524346719035ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__idle_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 779393143516309994ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__ld_key = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6963614551403125798ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1589548446467891707ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__kadd_2_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5957587211074898610ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12729017007867123829ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15766192500790063589ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2681792619302739304ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__state_idx = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 13147953693982476764ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__state_slice = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7272486059687875370ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0 = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9 = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10 = 0;
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3197816530539630023ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 220968667142219890ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 914214097670595347ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17732726588291592197ull);
    vlSelf->tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3 = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6554154646995524650ull);
    vlSelf->__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__Vfuncout = 0;
    vlSelf->__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__v = 0;
    vlSelf->__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__Vfuncout = 0;
    vlSelf->__Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__v = 0;
    vlSelf->__Vfunc_pad__8__Vfuncout = 0;
    vlSelf->__Vfunc_pad__8__in = 0;
    vlSelf->__Vfunc_pad__8__val = 0;
    vlSelf->__Vfunc_mask__9__Vfuncout = 0;
    vlSelf->__Vfunc_mask__9__in1 = 0;
    vlSelf->__Vfunc_mask__9__val = 0;
    vlSelf->__Vfunc_pad2__10__Vfuncout = 0;
    vlSelf->__Vfunc_pad2__10__in1 = 0;
    vlSelf->__Vfunc_pad2__10__in2 = 0;
    vlSelf->__Vfunc_pad2__10__val = 0;
    vlSelf->__Vfunc_mask__11__Vfuncout = 0;
    vlSelf->__Vfunc_mask__11__in1 = 0;
    vlSelf->__Vfunc_mask__11__val = 0;
    vlSelf->__Vfunc_pad__12__Vfuncout = 0;
    vlSelf->__Vfunc_pad__12__in = 0;
    vlSelf->__Vfunc_pad__12__val = 0;
    vlSelf->__Vdly__tb_verify__DOT__uut__DOT__rst_sh = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_verify__DOT__clk__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__tb_verify__DOT__reset_n__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__core_rst__0 = 0;
    vlSelf->__Vtrigprevexpr_h36b9350c__1 = 0;
    vlSelf->__Vtrigprevexpr_h9dc7e85d__1 = 0;
    vlSelf->__Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__ready_tag_pulse__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
