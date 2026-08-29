// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_verify.h for the primary calling header

#ifndef VERILATED_VTB_VERIFY___024ROOT_H_
#define VERILATED_VTB_VERIFY___024ROOT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"
#include "Vtb_verify___024root.h"


class Vtb_verify__Syms;
struct Vtb_verify_tb_verify__DOT__vector_t__struct__0 {
    QData/*63:0*/ __PVT__key1;
    QData/*63:0*/ __PVT__key2;
    QData/*63:0*/ __PVT__nonce1;
    QData/*63:0*/ __PVT__nonce2;
    VlWide<4>/*127:0*/ __PVT__exp;

    bool operator==(const Vtb_verify_tb_verify__DOT__vector_t__struct__0& rhs) const {
        return __PVT__key1 == rhs.__PVT__key1
            && __PVT__key2 == rhs.__PVT__key2
            && __PVT__nonce1 == rhs.__PVT__nonce1
            && __PVT__nonce2 == rhs.__PVT__nonce2
            && __PVT__exp == rhs.__PVT__exp;
    }
    bool operator!=(const Vtb_verify_tb_verify__DOT__vector_t__struct__0& rhs) const {
        return !(*this == rhs);
    }

    bool operator<(const Vtb_verify_tb_verify__DOT__vector_t__struct__0& rhs) const {
        return std::tie(__PVT__key1, __PVT__key2, __PVT__nonce1, __PVT__nonce2, __PVT__exp)
            <  std::tie(rhs.__PVT__key1, rhs.__PVT__key2, rhs.__PVT__nonce1, rhs.__PVT__nonce2, rhs.__PVT__exp);
    }
};
template <>
struct VlIsCustomStruct<Vtb_verify_tb_verify__DOT__vector_t__struct__0> : public std::true_type {};

class alignas(VL_CACHE_LINE_BYTES) Vtb_verify___024root final {
  public:

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        CData/*0:0*/ tb_verify__DOT__clk;
        CData/*0:0*/ tb_verify__DOT__reset_n;
        CData/*0:0*/ tb_verify__DOT__start;
        CData/*0:0*/ tb_verify__DOT__load_data;
        CData/*0:0*/ tb_verify__DOT__valid_data_in;
        CData/*0:0*/ tb_verify__DOT__last_block;
        CData/*4:0*/ tb_verify__DOT__valid_bytes;
        CData/*0:0*/ tb_verify__DOT__EOT;
        CData/*0:0*/ tb_verify__DOT__done_flag;
        CData/*2:0*/ tb_verify__DOT__uut__DOT__rst_sh;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__core_rst;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__core_key_valid;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__core_key_ready;
        CData/*7:0*/ tb_verify__DOT__uut__DOT__core_bdi_valid;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__core_bdi_ready;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__core_bdo_valid;
        CData/*3:0*/ tb_verify__DOT__uut__DOT__core_bdo_type;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__in_ad_window;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__in_msg_window;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__run_allow;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__run_active;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__done_r;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__launching;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__key_sel;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__npub_sel;
        CData/*4:0*/ tb_verify__DOT__uut__DOT__buf_vb;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__buf_eot;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__buf_last;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__buf_full;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__beat_hi;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__last_beat;
        CData/*7:0*/ tb_verify__DOT__uut__DOT__beat_mask;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__beat_consumed;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__msg_win_q;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__ct_beat_idx;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__tg_beat_idx;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__ready_tag_pulse;
        CData/*0:0*/ tb_verify__DOT__uut__DOT____VdfgExtracted_hbde8bc75__0;
        CData/*0:0*/ tb_verify__DOT__uut__DOT____VdfgExtracted_h3ab30db5__0;
        CData/*3:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__round_cnt_d;
        CData/*3:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__word_cnt_d;
        CData/*1:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__hash_cnt_d;
        CData/*4:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__fsm_d;
        CData/*4:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__fsm_q;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__auth_valid_d;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ad_eot_d;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ad_pad_d;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__eoi_d;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__mode_enc_dec;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__mode_hash_xof;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__idle_done;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ld_key;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ld_npub_done;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__kadd_2_done;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__abs_msg;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__ver_tag_done;
        CData/*3:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__state_idx;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____VdfgExtracted_hd4f75125__0;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_9;
        CData/*0:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____VdfgRegularize_h9ee191f3_0_10;
        CData/*7:0*/ __Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__Vfuncout;
        CData/*5:0*/ __Vfunc_tb_verify__DOT__uut__DOT__vb_mask__6__v;
        CData/*7:0*/ __Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__Vfuncout;
    };
    struct {
        CData/*5:0*/ __Vfunc_tb_verify__DOT__uut__DOT__vb_mask__7__v;
        CData/*7:0*/ __Vfunc_pad__8__val;
        CData/*7:0*/ __Vfunc_mask__9__val;
        CData/*7:0*/ __Vfunc_pad2__10__val;
        CData/*7:0*/ __Vfunc_mask__11__val;
        CData/*7:0*/ __Vfunc_pad__12__val;
        CData/*2:0*/ __Vdly__tb_verify__DOT__uut__DOT__rst_sh;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VstlPhaseResult;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_verify__DOT__clk__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_verify__DOT__reset_n__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__core_rst__0;
        CData/*0:0*/ __Vtrigprevexpr_h36b9350c__1;
        CData/*0:0*/ __Vtrigprevexpr_h9dc7e85d__1;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_verify__DOT__uut__DOT__ready_tag_pulse__0;
        CData/*0:0*/ __VactPhaseResult;
        CData/*0:0*/ __VinactPhaseResult;
        CData/*0:0*/ __VnbaPhaseResult;
        SData/*9:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_cnt_i__data_q;
        SData/*10:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_flags_i__data_q;
        SData/*10:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____Vcellinp__reg_flags_i__data_d;
        VlWide<4>/*127:0*/ tb_verify__DOT__data_in;
        VlWide<4>/*127:0*/ tb_verify__DOT__exp_ro;
        VlWide<4>/*127:0*/ tb_verify__DOT__simulated_ro;
        VlWide<4>/*127:0*/ tb_verify__DOT__latched_ct;
        VlWide<4>/*127:0*/ tb_verify__DOT__uut__DOT__buf_data;
        VlWide<4>/*127:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_key_i__data_q;
        VlWide<10>/*319:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____Vcellout__reg_state_i__data_q;
        IData/*31:0*/ __VactIterCount;
        IData/*31:0*/ __VinactIterCount;
        IData/*31:0*/ __Vi;
        QData/*63:0*/ tb_verify__DOT__key1;
        QData/*63:0*/ tb_verify__DOT__key2;
        QData/*63:0*/ tb_verify__DOT__nonce1;
        QData/*63:0*/ tb_verify__DOT__nonce2;
        QData/*63:0*/ tb_verify__DOT__latched_tag1;
        QData/*63:0*/ tb_verify__DOT__latched_tag2;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__core_bdo;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__ct_lo;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__ct_hi;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__tg1_r;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__tg2_r;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__1;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT____Vlvbound_h9f1a12f9__0;
        VlWide<4>/*127:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__key_d;
        VlWide<10>/*319:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__state_d;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__state_slice;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b2;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__b4;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c0;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c1;
        QData/*63:0*/ tb_verify__DOT__uut__DOT__u_core__DOT__asconp_i__DOT__g_leak__BRA__0__KET____DOT__u_leak__DOT__c3;
        QData/*63:0*/ __Vfunc_pad__8__Vfuncout;
        QData/*63:0*/ __Vfunc_pad__8__in;
        QData/*63:0*/ __Vfunc_mask__9__Vfuncout;
        QData/*63:0*/ __Vfunc_mask__9__in1;
        QData/*63:0*/ __Vfunc_pad2__10__Vfuncout;
        QData/*63:0*/ __Vfunc_pad2__10__in1;
        QData/*63:0*/ __Vfunc_pad2__10__in2;
        QData/*63:0*/ __Vfunc_mask__11__Vfuncout;
        QData/*63:0*/ __Vfunc_mask__11__in1;
        QData/*63:0*/ __Vfunc_pad__12__Vfuncout;
        QData/*63:0*/ __Vfunc_pad__12__in;
        VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
    };
    struct {
        VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggeredAcc;
        VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;
    };
    VlDelayScheduler __VdlySched;
    VlTriggerScheduler __VtrigSched_h2e47bcf5__0;
    VlTriggerScheduler __VtrigSched_hae8e2579__0;
    VlTriggerScheduler __VtrigSched_h096fd0ca__0;
    VlTriggerScheduler __VtrigSched_h8d3cb2b4__0;
    VlUnpacked<Vtb_verify_tb_verify__DOT__vector_t__struct__0, 5> tb_verify__DOT__vectors;

    // INTERNAL VARIABLES
    Vtb_verify__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_verify___024root(Vtb_verify__Syms* symsp, const char* namep);
    ~Vtb_verify___024root();
    VL_UNCOPYABLE(Vtb_verify___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};

std::string VL_TO_STRING(const Vtb_verify_tb_verify__DOT__vector_t__struct__0& obj);

#endif  // guard
