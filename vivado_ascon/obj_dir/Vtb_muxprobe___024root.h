// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_muxprobe.h for the primary calling header

#ifndef VERILATED_VTB_MUXPROBE___024ROOT_H_
#define VERILATED_VTB_MUXPROBE___024ROOT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"


class Vtb_muxprobe__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_muxprobe___024root final {
  public:

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        CData/*0:0*/ tb_muxprobe__DOT__clk;
        CData/*0:0*/ tb_muxprobe__DOT__reset_n;
        CData/*0:0*/ tb_muxprobe__DOT__start;
        CData/*0:0*/ tb_muxprobe__DOT__load_data;
        CData/*2:0*/ tb_muxprobe__DOT__uut__DOT__rst_sh;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__core_rst;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__core_key_valid;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__core_key_ready;
        CData/*7:0*/ tb_muxprobe__DOT__uut__DOT__core_bdi_valid;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__core_bdi_ready;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__core_bdo_valid;
        CData/*3:0*/ tb_muxprobe__DOT__uut__DOT__core_bdo_type;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__in_ad_window;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__in_msg_window;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__run_allow;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__run_active;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__launching;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__key_sel;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__npub_sel;
        CData/*4:0*/ tb_muxprobe__DOT__uut__DOT__buf_vb;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__buf_eot;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__buf_last;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__buf_full;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__beat_hi;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__last_beat;
        CData/*7:0*/ tb_muxprobe__DOT__uut__DOT__beat_mask;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__beat_consumed;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__tg_beat_idx;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0;
        CData/*3:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__round_cnt_d;
        CData/*3:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__word_cnt_d;
        CData/*1:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__hash_cnt_d;
        CData/*4:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__fsm_d;
        CData/*4:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__fsm_q;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__auth_valid_d;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__ad_eot_d;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__ad_pad_d;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__eoi_d;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__mode_enc_dec;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__mode_hash_xof;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__idle_done;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__ld_npub_done;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__kadd_2_done;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__abs_msg;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__ver_tag;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__ver_tag_done;
        CData/*3:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__state_idx;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9;
        CData/*0:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10;
        CData/*7:0*/ __Vfunc_tb_muxprobe__DOT__uut__DOT__vb_mask__3__Vfuncout;
        CData/*5:0*/ __Vfunc_tb_muxprobe__DOT__uut__DOT__vb_mask__3__v;
        CData/*7:0*/ __Vfunc_tb_muxprobe__DOT__uut__DOT__vb_mask__4__Vfuncout;
        CData/*5:0*/ __Vfunc_tb_muxprobe__DOT__uut__DOT__vb_mask__4__v;
        CData/*7:0*/ __Vfunc_pad__5__val;
        CData/*7:0*/ __Vfunc_mask__6__val;
        CData/*7:0*/ __Vfunc_pad2__7__val;
        CData/*7:0*/ __Vfunc_mask__8__val;
        CData/*7:0*/ __Vfunc_pad__9__val;
        CData/*2:0*/ __Vdly__tb_muxprobe__DOT__uut__DOT__rst_sh;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VstlPhaseResult;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_muxprobe__DOT__clk__0;
    };
    struct {
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_muxprobe__DOT__reset_n__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_muxprobe__DOT__uut__DOT__core_rst__0;
        CData/*0:0*/ __VactPhaseResult;
        CData/*0:0*/ __VinactPhaseResult;
        CData/*0:0*/ __VnbaPhaseResult;
        SData/*9:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q;
        SData/*10:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q;
        SData/*10:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d;
        VlWide<4>/*127:0*/ tb_muxprobe__DOT__uut__DOT__buf_data;
        VlWide<4>/*127:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q;
        VlWide<10>/*319:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q;
        IData/*31:0*/ __VactIterCount;
        IData/*31:0*/ __VinactIterCount;
        IData/*31:0*/ __Vi;
        QData/*63:0*/ tb_muxprobe__DOT__nonce2;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0;
        VlWide<4>/*127:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__key_d;
        VlWide<10>/*319:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__state_d;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__state_slice;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1;
        QData/*63:0*/ tb_muxprobe__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3;
        QData/*63:0*/ __Vfunc_pad__5__Vfuncout;
        QData/*63:0*/ __Vfunc_pad__5__in;
        QData/*63:0*/ __Vfunc_mask__6__in1;
        QData/*63:0*/ __Vfunc_pad2__7__Vfuncout;
        QData/*63:0*/ __Vfunc_pad2__7__in1;
        QData/*63:0*/ __Vfunc_pad2__7__in2;
        QData/*63:0*/ __Vfunc_mask__8__in1;
        QData/*63:0*/ __Vfunc_pad__9__Vfuncout;
        QData/*63:0*/ __Vfunc_pad__9__in;
        VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggeredAcc;
        VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;
    };
    VlDelayScheduler __VdlySched;
    VlTriggerScheduler __VtrigSched_hbf88aa0a__0;

    // INTERNAL VARIABLES
    Vtb_muxprobe__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_muxprobe___024root(Vtb_muxprobe__Syms* symsp, const char* namep);
    ~Vtb_muxprobe___024root();
    VL_UNCOPYABLE(Vtb_muxprobe___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
