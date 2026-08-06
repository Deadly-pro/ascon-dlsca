// ascon_params.sv
package ascon_params;

    // === Main parameters ===
    parameter int d          = 1;  // 0=unmasked(NEEDS CODE FIX), 1=2-share, 2=3-share
    parameter int PAR        = 22;
    parameter int COL_SIZE   = 5;
    parameter int WORD_SIZE  = 64;
    parameter int STATE_WIDTH = 320;

    // === Derived parameters ===
    parameter int num_shares = d + 1;
    parameter int SHIFT_PAR  = PAR;
    parameter int SHIFT_PAR_D_PLUS_1 = ((num_shares * PAR) > 64) ? 64 : (num_shares * PAR);

    parameter int SHIFT_PAR_LAST = (64 % SHIFT_PAR == 0) ? SHIFT_PAR : (64 % SHIFT_PAR);
    parameter int SHIFT_PAR_D_PLUS_1_LAST = (64 % SHIFT_PAR_D_PLUS_1 == 0) ? SHIFT_PAR_D_PLUS_1 : (64 % SHIFT_PAR_D_PLUS_1);

    parameter int NUMBER_BIT_MASK = ((64 + PAR - 1) / PAR) + 1;

    // NOTE: Fixed the ? : for NUMBER_BIT_NOMASK
    parameter int NUMBER_BIT_NOMASK = (64 % (PAR * num_shares) == 0) ? 
                                               ((64 + PAR * num_shares) / (PAR * num_shares) - 1) :
                                               ((64 + PAR * num_shares) / (PAR * num_shares));

    parameter int SHIFT_WIDTH = num_shares * PAR;
    /* verilator lint_off UNUSED */
    parameter int PADDED_WIDTH = ((WORD_SIZE + SHIFT_WIDTH - 1) / SHIFT_WIDTH) * SHIFT_WIDTH;
    parameter int RAND_WIDTH = d*COL_SIZE*PAR + (d+1)*d/2;
    /* verilator lint_on UNUSED */
    parameter int DATA_WIDTH       = RAND_WIDTH;
    parameter bit REVERSE          = 0;

    parameter int LFSR_WIDTH        = 31;
    parameter     LFSR_POLY         = 31'h10000001;
    parameter     LFSR_FEED_FORWARD = 0;

    // Configuration enums
    parameter int STYLE_AUTO      = 0;
    parameter int STYLE_LOOP      = 1;
    parameter int STYLE_REDUCTION = 2;

    parameter int CFG_FIBONACCI   = 0;
    parameter int CFG_GALOIS      = 1;

    // Scegli stile e configurazione
    parameter int STYLE = STYLE_LOOP;
    parameter int LFSR_CONFIG = CFG_FIBONACCI;

endpackage
