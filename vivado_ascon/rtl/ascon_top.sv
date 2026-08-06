/*
Il modulo ascon_top implementa l’intero datapath di un cifratore ASCON resistente ad attacchi side-channel, con mascheramento a d+1 condivisioni (per d=2) e supporto al parallelismo bit-level su PAR bit. La progettazione segue la logica dell’algoritmo ASCON-SCA, ma ne estende la configurabilità e il controllo hardware.

Componenti principali e funzionamento:
State Register (320 bit)
Il registro di stato gestisce l’evoluzione della cifratura. 
Supporta operazioni di shift configurabili (shift_type) e aggiornamento parallelo/multiplo (shift_en, write_en), 
sia per l’assorbimento dei dati sia per le permutazioni.

FSM di controllo (Mealy)
La macchina a stati controlla la sequenza operativa: inizializzazione, assorbimento del messaggio, padding, round permutativi, e generazione dell’output. Gestisce segnali di sincronizzazione e selezione (sel_*, reg_key*_load, ecc.).

Mascheramento e S-Box DOM
I dati vengono mascherati in d+1 domini indipendenti tramite un modulo shareCreator e trattati tramite una S-box resistiva agli attacchi di potenza (DOM – Domain-Oriented Masking). L’input alla S-box è trasformato da un primo layer affine; l’output subisce un secondo layer affine e viene poi ricombinato tramite uno XOR tree bit-wise.

Gestione round e costante RC
Ogni round applica una costante (round_constant) XORata a x2, con padding condizionato su tutti i registri se (d+1)*PAR > 64. 
L'interfaccia è progettata per adattarsi dinamicamente alle dimensioni di parallelismo.

Linear Diffusion Layer
Implementato secondo lo standard ASCON (rotazioni a, b), applica diffusione su ciascun word da 64 bit. È anche usato per la generazione del tag finale.

Padding e reversibilità dei dati
In fase di assorbimento, i messaggi sono sottoposti a padding standard (con 0x01) e sono gestiti byte-wise.
I dati sono invertiti nei byte prima di essere assorbiti, come da specifica ASCON.

Output e Tag
Il ciphertext è ottenuto da x0 e x1, mentre tag1 e tag2 sono derivati da x3 e x4 dopo diffusione lineare e XOR con le chiavi, secondo lo schema AEAD.

Debug e tracciamento
Il modulo espone numerosi segnali di debug (debug_state, roundcounter, bitcounter, contenuti dello stato, ecc.) per verifiche e simulazione,
particolarmente utili in fase di test SCA.

Il modulo è progettato per garantire robustezza contro attacchi di tipo DPA e flessibilità hardware,
risultando adatto a implementazioni ASIC o FPGA dove la sicurezza fisica è cruciale.
*/

// Import dei parametri ASCON
import ascon_params::d; // d : grado del mascheramento
import ascon_params::PAR; // PAR : parallelismo bit-level (numero S-BOX istanziato in parallelo)
import ascon_params::WORD_SIZE; // WORD_SIZE : dimensione della parola (64 bit)
import ascon_params::COL_SIZE; // COL_SIZE : dimensione della colonna (5 -> x0, x1, x2, x3, x4)
import ascon_params::STATE_WIDTH; // STATE_WIDTH : larghezza dello stato (320 bit) 
import ascon_params::SHIFT_PAR_D_PLUS_1; // SHIFT_PAR_D_PLUS_1 : shift per il parallelismo (d+1)*PAR -> numero shift per esecuzione non mascherata
import ascon_params::NUMBER_BIT_MASK;  // NUMBER_BIT_MASK : numero di bit da processare per round mascherato (64 bit /PAR bit) (estremo superiore)
import ascon_params::RAND_WIDTH; // RAND_WIDTH : numero di bit di casualità richiesti
import ascon_params::LFSR_WIDTH; // LFSR_WIDTH : larghezza dell'LFSR (31 bit)

module ascon_top (
    input  logic clk,
    input  logic reset_n,
    input  logic reset_n_lfsr, // serve per il TVLA (lfsr non viene resettato se do solo il software reset) -> se no ogni volta le maschere non cambierebbero
    input  logic start, 

    input  logic [WORD_SIZE-1:0] key1,
    input  logic [WORD_SIZE-1:0] key2,
    input  logic load_data, // settato a 1 una volta che ho i dati validi sugli input 

    input  logic [WORD_SIZE-1:0] nonce1,
    input  logic [WORD_SIZE-1:0] nonce2,
    input  logic [WORD_SIZE-1:0] initialVector,

    input  logic [2*WORD_SIZE-1:0] data_in, //input da 128 bit per blocchi di plaintext o associated data
    input  logic valid_data_in, // 1 se data_in è valido, 0 altrimenti
    input logic last_block,     // 1 segnale che sto ricevendo l'ultimo blocco di aad
    input logic [$clog2(2*WORD_SIZE/8):0] valid_bytes,  // numero di byte validi in data_in (0-16)
    input  logic EOT, //fine del messaggio in input (ultimo blocco di plaintext) -> posso iniziare la finalizzazione

    output logic [STATE_WIDTH-1:0] state_reg_out, //stato dello status register (320 bit)
    output logic ciphertext_valid, // 1 se il ciphertext di uscita è valido
    output logic [2*WORD_SIZE-1:0] ciphertext,
    output logic done, //se il processo è finito
    output logic ready_tag, // se il tag è pronto
    output logic [WORD_SIZE-1:0] tag1,
    output logic [WORD_SIZE-1:0] tag2,
    output logic ready_for_data, // se sono pronto a ricevere nuovi dati in input
    output logic read_data // ho letto i dati puoi iniziare a prepare i prossimi (su FPGA puoi salvare nei registri di input quelli nuovi)

    // Segnali di debug per ottenere il file debug_output.txt simile (uguale hopefully) a quello del golden model python:
    `ifdef DEBUG
        , //se c'è il debug
        output logic debug_extra_padding_ff,
        output logic [$clog2(NUMBER_BIT_MASK+1)-1:0] debug_bitcounter,
        output logic [3:0] debug_roundcounter,
        output logic [4:0] debug_state,
        output logic [63:0] debug_state_0,
        output logic [63:0] debug_state_1,
        output logic [63:0] debug_state_2,
        output logic [63:0] debug_state_3,
        output logic [63:0] debug_state_4,
        output logic [63:0] debug_round_state_0,
        output logic [63:0] debug_round_state_1,
        output logic [63:0] debug_round_state_2,
        output logic [63:0] debug_round_state_3,
        output logic [63:0] debug_round_state_4,
        output logic [63:0] debug_sbox_nomasked_0,
        output logic [63:0] debug_sbox_nomasked_1,
        output logic [63:0] debug_sbox_nomasked_2,
        output logic [63:0] debug_sbox_nomasked_3,
        output logic [63:0] debug_sbox_nomasked_4,
        output logic [63:0] debug_linear_diffusion_state3,
        output logic [63:0] debug_linear_diffusion_state4
    `endif
);

    //Associazione segnali di debug:
    `ifdef DEBUG
        assign debug_extra_padding_ff = extra_padding_ff;
        assign debug_bitcounter = bit_counter;
        assign debug_state_0 = state_reg_out[0*64 +: 64];
        assign debug_state_1 = state_reg_out[1*64 +: 64];
        assign debug_state_2 = state_reg_out[2*64 +: 64];
        assign debug_state_3 = state_reg_out[3*64 +: 64];
        assign debug_state_4 = state_reg_out[4*64 +: 64];
        assign debug_roundcounter = round_counter;
        assign debug_round_state_0 = round_x0_debug;
        assign debug_round_state_1 = round_x1_debug;
        assign debug_round_state_2 = round_x2_debug;
        assign debug_round_state_3 = round_x3_debug;
        assign debug_round_state_4 = round_x4_debug;
        assign debug_linear_diffusion_state3 = linear_diffusion_debug[3];
        assign debug_linear_diffusion_state4 = linear_diffusion_debug[4]; 
    `endif

    
    //segnali per LFSR:
    
    logic [RAND_WIDTH-1:0] lfsr_out; //output dell'LFSR
    logic [LFSR_WIDTH-1:0] lfsr_state_in;
    logic [LFSR_WIDTH-1:0] lfsr_state_out;
    
    // == istanzio LFSR (PRNG) ==
    lfsr lfst_inst (
        .data_in ({RAND_WIDTH{1'b0}}),
        .state_in    (lfsr_state_in),
        .state_out   (lfsr_state_out),
        .data_out    (lfsr_out)
    );
    //segnali di randomicità :
    logic [d*COL_SIZE*PAR-1:0] random_masks; //maschere casuali per la creazione delle shares

    /* verilator lint_off UNUSED */ //Per il changing of the guards non le utilizzo
    logic [(d+1)*d/2-1:0] random_masks_sbox; //maschere casuali per la s-box
    /* verilator lint_on UNUSED */
    assign random_masks = lfsr_out[0+:d*COL_SIZE*PAR]; //prendo i primi d*COL_SIZE*PAR bit dell'LFSR per lo share-creator
    assign random_masks_sbox = lfsr_out[d*COL_SIZE*PAR+:((d+1)*d/2)]; //prendo i successivi (d+1)*d/2 bit dell'LFSR per s-box

    // reset dell'LFSR: NOTA BENE -> ha un reset diverso per svolgere il TVLA (se usiamo il reset software l'LFSR non viene resettato)
    // un'altra possibilità sarebbe stata quella di resettare anche LFSR, ma caricare un seed casuale dall'esterno, ogni volta (dovevo cambiare più cose)
    always_ff @(posedge clk or negedge reset_n_lfsr) begin
    if (!reset_n_lfsr) 
        lfsr_state_in <= 31'h1234567;  // seed fisso
    else
        lfsr_state_in <= lfsr_state_out;
    end

    //segnali per FSM:
    logic extra_padding_ff; //se devo fare il padding extra (ossia l'ultimo blocco di msg (aad o plaintext) è di dimensione 16 byte esatti)
    logic shift_en, shift_type, write_en; // shift_type mi dice se devo shiftare di PAR bit o di (d+1)*PAR bit
    logic last_cycle; // se sono all'ultimo ciclo di shift (posso shiftare un numero diverso di bit a secondo di quando fa 64 % shift_pos)
    logic reg_key1_load, reg_key2_load;
    logic sel_mux_linear_diffusion_out_x3, sel_mux_linear_diffusion_out_x4;  // prima di iniziare la finalizzazione devo fare l'xor fra l'output del LDL e la chiave
    logic sel_init_load, sel_masked_round, sel_padding, sel_xor_signal, sel_absorb_data; // segnali per i mux di selezione (caricare input in status_reg)
    logic [3:0] round_counter; // contatore dei round di permutazione masked :(0-12), unmasked : (4-12) -> NOTA: non (0-8) se no la RC  
    logic unsigned [$clog2(NUMBER_BIT_MASK+1)-1:0] bit_counter; // contatore dei bit da processare per round mascherato masked: ((64 / PAR)  + 2) estremo superiore {2 stadi di FF}; unmasked : (64 / PAR + 1) estremo superiore

    `ifdef DEBUG
        logic shift_enable_sipo, last_cycle_sipo;  // segnali per il sipo debug
    `endif


    // === Istanzio fsm === (Zamboni non sarebbe contento)
    fsm mealy_fsm (
        //Input:
        .clk(clk),
        .reset_n(reset_n),
        .start(start),

        .load_data(load_data),
        .valid_data_in(valid_data_in),
        .last_block(last_block),
        .valid_bytes(valid_bytes),
        .EOT(EOT),

        //Output dell'interfaccia:
        .done(done),
        .tag_valid(ready_tag),
        .ready_for_data(ready_for_data),
        .read_data(read_data),
        .ciphertext_valid(ciphertext_valid),

        //Output esclusivi della fsm:
        .shift_en(shift_en),
        .write_en(write_en),
        .shift_type(shift_type),
        .last_cycle(last_cycle),
        .reg_key1_load(reg_key1_load),
        .reg_key2_load(reg_key2_load),

        .sel_mux_linear_diffusion_out_x3(sel_mux_linear_diffusion_out_x3),
        .sel_mux_linear_diffusion_out_x4(sel_mux_linear_diffusion_out_x4),
        .sel_init_load(sel_init_load),
        .sel_masked_round(sel_masked_round),
        .sel_padding(sel_padding),
        .sel_xor_signal(sel_xor_signal),
        .sel_absorb_data(sel_absorb_data),
        .extra_padding_ff(extra_padding_ff),
        .round_counter(round_counter),
        .bit_counter(bit_counter)

        `ifdef DEBUG
            ,
            .debug_state(debug_state),
            .shift_enable_sipo(shift_enable_sipo),
            .last_cycle_sipo(last_cycle_sipo)
        `endif
    );

    //Segnali per lo state_register: 
    logic [STATE_WIDTH-1:0] state_reg_in_shares [d:0]; //input del registro di stato
    logic [SHIFT_PAR_D_PLUS_1*COL_SIZE-1:0] state_reg_out_shiftdplus1_shares [d:0];  //uscita shift = parallelismo*(d+1)
    logic [SHIFT_PAR_D_PLUS_1*COL_SIZE-1:0] state_reg_in_shiftdplus1_shares [d:0];  //input shift = parallelismo*(d+1)
    logic [PAR*COL_SIZE-1:0] state_reg_in_shift1_shares [d:0]; //input shift = PAR bit 
    logic [STATE_WIDTH-1:0]  state_reg_out_shares [d:0]; //output del registro di stato

    // == Istanzio state_register == NOTA BENE: ne servono più di uno perchè devo ricombinare le shares dopo averle salvate se no sarei vulnerabili ad attacchi sul contenuto dello state register
    genvar s;

    generate
        for (s = 0; s <= d; s++) begin : gen_state_regs

            localparam logic write_en_i = (s == 1 || s == 2) ? 1'b0 : 1'b1;

            state_register state_reg_share (
                .clk(clk),
                .reset_n(reset_n),
                .write_en(write_en & write_en_i), //Il parallel load è attivo solo per uno state register, gli altri sono solo shift registers -> Possibile ottimizzazione
                .shift_en(shift_en),
                .shift_type(shift_type),
                .last_cycle(last_cycle),
                .data_in(state_reg_in_shares[s]), 
                .in_shifted_dplus1(state_reg_in_shiftdplus1_shares[s]), 
                .in_shifted_1bit(state_reg_in_shift1_shares[s]),      
                .out_shifted_dplus1(state_reg_out_shiftdplus1_shares[s]),
                .data_out(state_reg_out_shares[s]) 
            );
        end
    endgenerate

    assign state_reg_out = state_reg_out_shares[0]; //output dello stato del registro di stato, prendo il primo dominio (A)

    //Register per la chiave (key1):
    logic [WORD_SIZE-1:0] reg_key1_out;

    // == Istanzio il registro per la chiave 1 ==
    register key1_reg (
        .clk(clk),
        .reset_n(reset_n),
        .load(reg_key1_load),
        .data_in(key1),
        .data_out(reg_key1_out)
    );

    //Register per la chiave (key2):
    logic [WORD_SIZE-1:0] reg_key2_out;

    // == Istanzio il registro per la chiave 2 ==
    register key2_reg (
        .clk(clk),
        .reset_n(reset_n),
        .load(reg_key2_load),
        .data_in(key2),
        .data_out(reg_key2_out)
    );

    `ifdef DEBUG
        logic [WORD_SIZE-1:0] round_x0_debug, round_x1_debug, round_x2_debug, round_x3_debug, round_x4_debug;

        //5 shift register d'uscita per leggere i dati in maniera comoda (solo per DEBUG) -> mi servono per costruire il risultato del RC operation:
        sipo_debug sipo_reg_x0_debug (
            .clk(clk),
            .reset_n(reset_n),
            .shift_en(shift_enable_sipo),
            .in_shifted_dplus1(mux_1st_x0[0+:SHIFT_PAR_D_PLUS_1]),
            .in_shifted_1bit(mux_1st_x0[0+:PAR]),
            .shift_type(shift_type),
            .last_cycle(last_cycle_sipo),
            .data_out(round_x0_debug)
        );

        sipo_debug sipo_reg_x1_debug (
            .clk(clk),
            .reset_n(reset_n),
            .shift_en(shift_enable_sipo),
            .in_shifted_dplus1(mux_1st_x1[0+:SHIFT_PAR_D_PLUS_1]),
            .in_shifted_1bit(mux_1st_x1[0+:PAR]),
            .last_cycle(last_cycle_sipo),
            .shift_type(shift_type),
            .data_out(round_x1_debug)
        );

        sipo_debug sipo_reg_x2_debug (
            .clk(clk),
            .reset_n(reset_n),
            .shift_en(shift_enable_sipo),
            .in_shifted_dplus1(mux_1st_x2[0+:SHIFT_PAR_D_PLUS_1]),
            .in_shifted_1bit(mux_1st_x2[0+:PAR]),
            .last_cycle(last_cycle_sipo),
            .shift_type(shift_type),
            .data_out(round_x2_debug)
        );

        sipo_debug sipo_reg_x3_debug (
            .clk(clk),
            .reset_n(reset_n),
            .shift_en(shift_enable_sipo),
            .in_shifted_dplus1(mux_1st_x3[0+:SHIFT_PAR_D_PLUS_1]),
            .in_shifted_1bit(mux_1st_x3[0+:PAR]),
            .last_cycle(last_cycle_sipo),
            .shift_type(shift_type),
            .data_out(round_x3_debug)
        );

        sipo_debug sipo_reg_x4_debug (
            .clk(clk),
            .reset_n(reset_n),
            .shift_en(shift_enable_sipo),
            .in_shifted_dplus1(mux_1st_x4[0+:SHIFT_PAR_D_PLUS_1]),
            .in_shifted_1bit(mux_1st_x4[0+:PAR]),
            .last_cycle(last_cycle_sipo),
            .shift_type(shift_type),
            .data_out(round_x4_debug)
        );

    `endif


    // Input Network : divido i segnali nelle 5 componenti: x0,x1,x2,x3,x4 (per comodità)
    // state_reg_out_xi è un array di PAR*(d+1) bit
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x0; 
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x1; 
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x2; 
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x3; 
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x4; 

    //Lo status register in cui carico i dati dall'esterno è [0] (gli altri li uso solo per conservare le shares)
    assign state_reg_out_x0 = state_reg_out_shiftdplus1_shares[0][0+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x1 = state_reg_out_shiftdplus1_shares[0][SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x2 = state_reg_out_shiftdplus1_shares[0][2*SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x3 = state_reg_out_shiftdplus1_shares[0][3*SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x4 = state_reg_out_shiftdplus1_shares[0][4*SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];

    //b) applico ai vari segnali la RC:
    // In teoria basterebbe solo per x2 ma se PAR*(d+1) > 64 faccio anche il padding di 00 sugli altri segnali
    logic [(d+1)*PAR-1:0] mux_1st_x0;
    logic [(d+1)*PAR-1:0] mux_1st_x1;
    logic [(d+1)*PAR-1:0] mux_1st_x2;
    logic [(d+1)*PAR-1:0] mux_1st_x3;
    logic [(d+1)*PAR-1:0] mux_1st_x4;

    // === Round constant handling ===

    // Costante di round a 64 bit: viene calcolata sottraendo 0x0F * round_counter da 0xF0
    logic [63:0] round_constant_full;
    assign round_constant_full = 64'hF0 - (64'h0F * round_counter);

    // Arrotonda a multipli di PAR per permettere uno slicing regolare (zero-padding a sinistra)
    localparam int RC_PADDED_WIDTH = ((64 + PAR - 1) / PAR) * PAR;
    logic [RC_PADDED_WIDTH-1:0] round_constant_padded;
    assign round_constant_padded = { {(RC_PADDED_WIDTH - 64){1'b0}}, round_constant_full };

    // === Selezione della costante di round per ogni condivisione (share) ===

    // Vettore di costanti per ogni share (d+1 condivisioni, ognuna larga PAR bit)
    logic [PAR-1:0] rc_block[d:0];

    genvar i_input_net;
    generate
        for (i_input_net = 0; i_input_net < d+1; i_input_net++) begin : mux_logic

            // Se sel_masked_round è attivo, ho solo un'uscita di PAR bit che mi interessa dallo status register 
            // Altrimenti, leggo (d+1)*PAR bit ognuno dei quali deve ricevere una fetta diversa della RC
            
            /*assign rc_block[i_input_net] = (sel_masked_round) 
                        ? round_constant_padded[unsigned'((bit_counter * PAR)) +: PAR]
                        : round_constant_padded[unsigned'((unsigned'((d+1)) * unsigned'(bit_counter) * PAR) + unsigned'((i_input_net * PAR))) +: PAR];
            */
            localparam int BIT_COUNTER_MAX_FULL = NUMBER_BIT_MASK - 1;
            localparam [$clog2(NUMBER_BIT_MASK+1)-1:0]  BIT_COUNTER_MAX = BIT_COUNTER_MAX_FULL[$clog2(NUMBER_BIT_MASK+1)-1:0];
            /*always_comb begin
                logic [PAR-1:0] rc_block_temp;
                if (bit_counter <  BIT_COUNTER_MAX) begin //NOTA QUESTO IF NON C'ERA ERA PER TOGLIERE DELLE X
                    assign rc_block_temp = (sel_masked_round) 
                        ? round_constant_padded[unsigned'((bit_counter * PAR)) +: PAR]
                        : round_constant_padded[unsigned'((unsigned'((d+1)) * unsigned'(bit_counter) * PAR) + unsigned'((i_input_net * PAR))) +: PAR];
                end else begin
                    assign rc_block_temp = '0;
                end
                rc_block[i_input_net] = rc_block_temp;
            end */
            always_comb begin
                logic [PAR-1:0] rc_block_temp;
                if (bit_counter < BIT_COUNTER_MAX) begin
                    if (sel_masked_round) begin
                        rc_block_temp = round_constant_padded[(bit_counter * PAR) +: PAR];
                    end else begin
                        rc_block_temp = round_constant_padded[(((d+1) * bit_counter * PAR) + (i_input_net * PAR)) +: PAR];
                    end
                end else begin
                    rc_block_temp = '0;
                end
                rc_block[i_input_net] = rc_block_temp;
            end
            // === Applicazione della costante RC a x2, e propagazione degli altri stati ===

            // Caso normale: se PAR*(d+1) <= 64, possiamo usare tutti i bit direttamente
            if (PAR*(d+1) <= 64) begin : gen_normal
                assign mux_1st_x0[i_input_net*PAR+:PAR] = state_reg_out_x0[i_input_net*PAR+:PAR];
                assign mux_1st_x1[i_input_net*PAR+:PAR] = state_reg_out_x1[i_input_net*PAR+:PAR];
                assign mux_1st_x2[i_input_net*PAR+:PAR] = state_reg_out_x2[i_input_net*PAR+:PAR] ^ rc_block[i_input_net]; // solo x2 XORa con RC
                assign mux_1st_x3[i_input_net*PAR+:PAR] = state_reg_out_x3[i_input_net*PAR+:PAR];
                assign mux_1st_x4[i_input_net*PAR+:PAR] = state_reg_out_x4[i_input_net*PAR+:PAR];

            end else begin : gen_padded
                // Caso in cui PAR*(d+1) > 64: ultima slice potrebbe avere meno di PAR bit validi

                if (i_input_net < d) begin : gen_body
                    // Le prime d condivisioni sono piene → usa PAR bit direttamente
                    assign mux_1st_x0[i_input_net*PAR+:PAR] = state_reg_out_x0[i_input_net*PAR+:PAR];
                    assign mux_1st_x1[i_input_net*PAR+:PAR] = state_reg_out_x1[i_input_net*PAR+:PAR];
                    assign mux_1st_x2[i_input_net*PAR+:PAR] = state_reg_out_x2[i_input_net*PAR+:PAR] ^ rc_block[i_input_net];
                    assign mux_1st_x3[i_input_net*PAR+:PAR] = state_reg_out_x3[i_input_net*PAR+:PAR];
                    assign mux_1st_x4[i_input_net*PAR+:PAR] = state_reg_out_x4[i_input_net*PAR+:PAR];

                end else begin : gen_last
                    // Ultima condivisione → potenzialmente contiene meno di PAR bit
                    localparam int LAST_PAR_USED = 64 - (d * PAR); // quanti bit effettivi sono rimasti da usare

                    // Si zero-paddano i bit superiori non validi
                    assign mux_1st_x0[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x0[i_input_net*PAR+:LAST_PAR_USED] };
                    assign mux_1st_x1[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x1[i_input_net*PAR+:LAST_PAR_USED] };
                    assign mux_1st_x2[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x2[i_input_net*PAR+:LAST_PAR_USED] } ^ rc_block[i_input_net];
                    assign mux_1st_x3[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x3[i_input_net*PAR+:LAST_PAR_USED] };
                    assign mux_1st_x4[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x4[i_input_net*PAR+:LAST_PAR_USED] };
                end
            end
        end
    endgenerate


    // === Creazione delle shares ===

    logic [(d+1)*PAR*COL_SIZE-1:0] shares_out; 
    logic [PAR*COL_SIZE-1:0] shares_in; 
    //Ho bisogno di selezionare i 5*PAR bit della prima input network, quindi i primi PAR di ogni componente (le shares mi servono solo per il masked round):
    assign shares_in = {mux_1st_x4[0+:PAR], mux_1st_x3[0+:PAR], mux_1st_x2[0+:PAR], mux_1st_x1[0+:PAR], mux_1st_x0[0+:PAR]}; 
    
    //Istanzio il modulo shareCreator che crea le d+1 condivisioni per ogni componente (x0,x1,x2,x3,x4):
    shareCreator share_creator(
        .data_in(shares_in),
        .random_masks(random_masks),
        .shares_out(shares_out)
    );

    //multiplexer per gestire l'ingresso della S-Box (prendo le shares oppure le d+1 colonne diverse):
    logic [PAR*COL_SIZE-1:0] affine_layer_in [d:0];

    genvar i_affine;
    generate
        //Assegnazione dei vari domini (devo dividere i dati sui vari domini, ognuno dei quali avrà 5*PAR bit)
        // i_affine è il dominio (A,B,C)
        for (i_affine = 0; i_affine < d+1; i_affine++) begin : gen_affine_assign
            assign affine_layer_in[i_affine] = (sel_masked_round) 
            //Devo selezionare le shares: x0_sharesA, x1_sharesA, x2_sharesA, x3_sharesA, x4_sharesA e poi x0_sharesB etc.
            ? {shares_out[i_affine*PAR*COL_SIZE+:PAR*COL_SIZE]} 
            //Devo selezionare le d+1 colonne diverse in uscita dalle input network:
            : {mux_1st_x4[i_affine*PAR+:PAR], mux_1st_x3[i_affine*PAR+:PAR], mux_1st_x2[i_affine*PAR+:PAR], mux_1st_x1[i_affine*PAR+:PAR], mux_1st_x0[i_affine*PAR+:PAR]};
        end
    endgenerate

    // === First layer affine ===

    //devo applicare il first affine layer su ogni dominio [i]:
    //1st affine layer -> x0 = x0 ^ x4, x2 = x2 ^ x1, x4 = x4 ^ x3
    logic [PAR*COL_SIZE-1:0] affine_layer_out [d:0];

    genvar i_affine_out;
    generate
        for (i_affine_out = 0; i_affine_out< d+1; i_affine_out++) begin : affine_layer_1st
            assign affine_layer_out[i_affine_out] = {
                affine_layer_in[i_affine_out][4*PAR+:PAR] ^ affine_layer_in[i_affine_out][3*PAR+:PAR], 
                affine_layer_in[i_affine_out][3*PAR+:PAR],
                affine_layer_in[i_affine_out][2*PAR+:PAR] ^ affine_layer_in[i_affine_out][PAR+:PAR], 
                affine_layer_in[i_affine_out][PAR+:PAR], 
                affine_layer_in[i_affine_out][0+:PAR] ^ affine_layer_in[i_affine_out][4*PAR+:PAR]
            };
        end
    endgenerate

    //Mi serve input s-box diviso in PAR array da 5*d+1 bit:
    logic [(d+1)*COL_SIZE-1:0] next_sbox_input [PAR-1:0]; // ho un layer di FF in ingresso alla s-box
    genvar i_sbox, p_sbox;
    generate
        for (p_sbox=0; p_sbox < PAR; p_sbox++) begin : sbox_input_gen
            for (i_sbox=0; i_sbox < d+1; i_sbox++) begin
                //assegno i valori di x0 divisi su 1 bit (da PAR -> 1 bit), mettendo in maniera consecutiva x0_A, x0_B, etc.
                //ora li ho divisi per dominio (x0_A, x1_A, x2_A, x3_A, x4_A, x0_B, x1_B, etc.) ora li voglio per componente (x0_A, x0_B, x0_C, etc.)
                assign next_sbox_input[p_sbox][i_sbox] = affine_layer_out[i_sbox][p_sbox]; 
                //stessa cosa per x1:
                assign next_sbox_input[p_sbox][(d+1)+i_sbox] = affine_layer_out[i_sbox][PAR+p_sbox];
                //stessa cosa per x2:
                assign next_sbox_input[p_sbox][2*(d+1)+i_sbox] = affine_layer_out[i_sbox][2*PAR+p_sbox];
                //stessa cosa per x3:
                assign next_sbox_input[p_sbox][3*(d+1)+i_sbox] = affine_layer_out[i_sbox][3*PAR+p_sbox];
                //stessa cosa per x4:
                assign next_sbox_input[p_sbox][4*(d+1)+i_sbox] = affine_layer_out[i_sbox][4*PAR+p_sbox];
            end
        end
    endgenerate

    //creazione dei segnali per s-box:
    logic [(d+1)*COL_SIZE-1:0] sbox_input[PAR-1:0];     //input della s-box
    logic [(d+1)*COL_SIZE-1:0] sbox_output[PAR-1:0];    //output della s-box
    logic [(d+1)*COL_SIZE-1:0] sbox_output_unmasked[PAR-1:0];  //output della s-box non mascherato
    // flip flop per garantire l'indipendenza degli ingressi della DOM-AND:
    always_ff @(posedge clk) begin
        for (int p = 0; p < PAR; p++) begin
            sbox_input[p] <= next_sbox_input[p];
        end
    end
   

    //collego gli input alla s-box, vorrei usare il changing of the guards:
    //NOTA IL CHANGING OF THE GUARDS E' SUPPORTATO SOLO PER IL GRADO 1 e 2 (in questo codice)
    
    genvar p;
    generate
        if (d == 2) begin : gen_cog //changing of the guards disabilitatio (d == 2)
            
            for (p = 0; p < PAR; p++) begin : gen_sbox
                // la fresh_r è corretta per il changing of the guards perchè i bit all'interno dello status reg sono già shiftati
                logic [(d+1)*d/2-1:0] fresh_r;
                assign fresh_r = { state_reg_out[(35+p)%64], state_reg_out[(37+p)%64], state_reg_out[(11+p)%64]  };
                ascon_sbox_d2 u_sbox (
                    .clk(clk),
                    .x_in(sbox_input[p]),
                    .fresh_r(fresh_r),
                    .sel_masked_round(sel_masked_round),
                    .x_out(sbox_output[p]),
                    .x_out_noMask(sbox_output_unmasked[p])
                );
            end
        end else if (d == 1) begin : gen_no_cog //changing of the guards disabilitatio (d == 1)
            for (p = 0; p < PAR; p++) begin : gen_sbox
                logic [(d+1)*d/2-1:0] fresh_r;
                assign fresh_r = state_reg_out[(11+p)%64];
                ascon_sbox_d2 u_sbox (
                    .clk(clk),
                    .x_in(sbox_input[p]),
                    .fresh_r(fresh_r),
                    .sel_masked_round(sel_masked_round),
                    .x_out(sbox_output[p]),
                    .x_out_noMask(sbox_output_unmasked[p])
                );
            end
        end else begin : gen_no_changing
            for (p = 0; p < PAR; p++) begin : gen_sbox
                logic [(d+1)*d/2-1:0] fresh_r;
                assign fresh_r = random_masks_sbox;
                ascon_sbox_d2 u_sbox (
                    .clk(clk),
                    .x_in(sbox_input[p]),
                    .fresh_r(fresh_r),
                    .sel_masked_round(sel_masked_round),
                    .x_out(sbox_output[p]),
                    .x_out_noMask(sbox_output_unmasked[p])
                );
            end
        end
    endgenerate

    //mux selezione fra output mascherato e non mascherato dalla S-BOX:
    logic [(d+1)*COL_SIZE-1:0] mux_sbox_out [PAR-1:0];
    assign mux_sbox_out = (sel_masked_round) ? sbox_output : sbox_output_unmasked;

    //devo riconvertire i segnali per l'affine layer (separazione sui domini A,B, C etc.), inverso di quanto fatto prima:
    logic [PAR*COL_SIZE-1:0] affine_layer2nd_in [d:0]; // 
    genvar i_2ndAffine, p_2ndAffine;

    generate
        for (i_2ndAffine = 0; i_2ndAffine < d+1; i_2ndAffine++) begin : gen_affine2nd
            for (p_2ndAffine = 0; p_2ndAffine < PAR; p_2ndAffine++) begin : gen_bit
                assign affine_layer2nd_in[i_2ndAffine][p_2ndAffine]           = mux_sbox_out[p_2ndAffine][i_2ndAffine];                 // x0_i[p]
                assign affine_layer2nd_in[i_2ndAffine][PAR + p_2ndAffine]     = mux_sbox_out[p_2ndAffine][(d+1) + i_2ndAffine];         // x1_i[p]
                assign affine_layer2nd_in[i_2ndAffine][2*PAR + p_2ndAffine]   = mux_sbox_out[p_2ndAffine][2*(d+1) + i_2ndAffine];       // x2_i[p]
                assign affine_layer2nd_in[i_2ndAffine][3*PAR + p_2ndAffine]   = mux_sbox_out[p_2ndAffine][3*(d+1) + i_2ndAffine];       // x3_i[p]
                assign affine_layer2nd_in[i_2ndAffine][4*PAR + p_2ndAffine]   = mux_sbox_out[p_2ndAffine][4*(d+1) + i_2ndAffine];       // x4_i[p]
            end
        end
    endgenerate

    // == Second affine layer ==

    logic [PAR*COL_SIZE-1:0] affine_layer2nd_out[d:0];
    genvar i_2ndAff_out; //i: sono i diversi domini
    generate

        
        for (i_2ndAff_out = 0; i_2ndAff_out < d+1; i_2ndAff_out++) begin : affine_layer
            
            logic [PAR-1:0] affine_layer2nd_in_temp;
            //Se ho un numero di shares pari devo invertire solo x2 del primo share, altrimenti l'effetto si annulla
            always_comb begin
                if ((d % 2) == 1 && i_2ndAff_out > 0 && sel_masked_round == 1)
                    affine_layer2nd_in_temp = affine_layer2nd_in[i_2ndAff_out][2*PAR+:PAR];
                else
                    affine_layer2nd_in_temp = ~affine_layer2nd_in[i_2ndAff_out][2*PAR+:PAR];
            end

            assign affine_layer2nd_out[i_2ndAff_out] = {
                affine_layer2nd_in[i_2ndAff_out][4*PAR+:PAR],
                affine_layer2nd_in[i_2ndAff_out][3*PAR+:PAR] ^ affine_layer2nd_in[i_2ndAff_out][2*PAR+:PAR],
                affine_layer2nd_in_temp,
                affine_layer2nd_in[i_2ndAff_out][PAR+:PAR] ^ affine_layer2nd_in[i_2ndAff_out][0+:PAR],
                affine_layer2nd_in[i_2ndAff_out][0+:PAR] ^ affine_layer2nd_in[i_2ndAff_out][4*PAR+:PAR]
            };
        end
    endgenerate

    // == Recombination of shares after affine layer == 
    // Serve per avere il risultato della S-Box in fase di debug, per vedere se le condivisioni sono corrette
    `ifdef DEBUG
        logic [STATE_WIDTH-1:0] recombine_shares_sbox;
        generate
            for (genvar bit_idx_sbox = 0; bit_idx_sbox < STATE_WIDTH; bit_idx_sbox++) begin : recombine
                // Per ogni bit (posizione) ricombina il valore proveniente da tutti i domini (d+1)
                logic [d:0] temp_bits_sbox;
                
                always_comb begin
                    for (int st_reg_sbox = 0; st_reg_sbox <= d; st_reg_sbox++) begin
                        temp_bits_sbox[st_reg_sbox] = state_reg_out_shares[st_reg_sbox][bit_idx_sbox];
                    end
                    recombine_shares_sbox[bit_idx_sbox] = xor_tree(temp_bits_sbox, d+1);
                end
            end
        endgenerate
        
        assign debug_sbox_nomasked_0 = recombine_shares_sbox[0*64 +: 64];
        assign debug_sbox_nomasked_1 = recombine_shares_sbox[1*64 +: 64];
        assign debug_sbox_nomasked_2 = recombine_shares_sbox[2*64 +: 64];
        assign debug_sbox_nomasked_3 = recombine_shares_sbox[3*64 +: 64];
        assign debug_sbox_nomasked_4 = recombine_shares_sbox[4*64 +: 64];
    `endif
    

    //Assegno le entrate seriali dello state register (mascherate e non): 
    //Ingresso Mascherato: salvo ogni shares (PAR*COL_SIZE bits) nel suo registro:
    always_comb begin
        for (int st = 0; st <= d; st++) begin
            state_reg_in_shift1_shares[st] = affine_layer2nd_out[st];
        end
    end

    //Ingresso non masherato: (d+1)*PAR*COL_SIZE bits -> lo salvo nello state_reg[0], non ho bisogno degli altri registri non ho condivisioni!
    generate
        if ((PAR * (d + 1)) <= 64) begin : gen_normal
            for (genvar idx = 0; idx < COL_SIZE; idx++) begin : pack_affine
                for (genvar d_idx = 0; d_idx < d+1; d_idx++) begin : pack_affine_int
                    assign state_reg_in_shiftdplus1_shares[0][idx*PAR*(d+1)+PAR*d_idx +: PAR] =
                        affine_layer2nd_out[d_idx][idx*PAR +: PAR];
                end
            end
        end else begin : gen_truncate
            for (genvar idx = 0; idx < COL_SIZE; idx++) begin : pack_affine_trunc
                for (genvar d_idx = 0; d_idx < d+1; d_idx++) begin : pack_affine_trunc_int
                    if (PAR * d_idx < 64) begin : active_bits
                        localparam int USED_BITS = ((PAR * (d_idx + 1)) <= 64) ? PAR : (64 - PAR * d_idx);
                        assign state_reg_in_shiftdplus1_shares[0][idx*64 + PAR*d_idx +: USED_BITS] =
                            affine_layer2nd_out[d_idx][idx*PAR +: USED_BITS];
                    end
                    // Altrimenti non assegno nulla → padding implicito a 0
                end
            end
        end
    endgenerate

    //Definizione dei possibili state_in (su 320 bit) del registro di stato:
    logic [WORD_SIZE-1:0] state_reg_in_absorb[4:0]; //bypass per il registro di stato (serve per l'assorbimento di MSG o AD)
    logic [STATE_WIDTH-1:0] init_data; //concatenazione input (IV, key1, key2, nonce1, nonce2)
    logic [STATE_WIDTH-1:0] linear_diffusion_out; //uscita del layer di diffusione lineare

    // == Gestione del padding ==
    logic [2*WORD_SIZE-1:0] data_in_padded;

    always_comb begin
        if (extra_padding_ff)  begin//se c'è un padding extra) begin
            data_in_padded = '0;
            data_in_padded = {8'h01, {(2*WORD_SIZE-8){1'b0}}};
        end
        else if (sel_padding) begin
            data_in_padded = '0;
            // Copia i byte validi nei primi byte:
            for (int unsigned i = 0; i < 16; i++) begin
                if (i < valid_bytes)
                    data_in_padded[127 - i*8 -: 8] = data_in[127 - i*8 -: 8];
            end

            // Inserisci il padding (0x01) subito dopo l'ultimo byte valido
            data_in_padded[(127 - valid_bytes*8) -: 8] = 8'h01;
        end else begin
            data_in_padded = data_in;
        end
    end

    logic [2*WORD_SIZE-1:0] reverse_reg_data_out; //bypass per il registro di stato

    // Funzione per invertire i byte di un input a 128 bit (2*WORD_SIZE) INVERTE L'ENDIANESS (non era strettamente necessaria)
    function automatic logic [2*WORD_SIZE-1:0] reverse_bytes(input logic [2*WORD_SIZE-1:0] x);
        logic [2*WORD_SIZE-1:0] y;
        for (int i = 0; i < 8; i++) begin
            y[i*8 +: 8] = x[(7-i)*8 +: 8];
            y[i*8 + WORD_SIZE +: 8] = x[(7-i)*8 + WORD_SIZE +: 8];
        end
        return y;
    endfunction

    //selezione tra i dati in ingresso e il padding:
    assign reverse_reg_data_out = (sel_padding) ? reverse_bytes(data_in_padded) : reverse_bytes(data_in);

    //Absorb di MSG o AD:
    assign state_reg_in_absorb[0] = state_reg_out[0+:WORD_SIZE] ^ reverse_reg_data_out[WORD_SIZE+:WORD_SIZE];
    assign state_reg_in_absorb[1] = state_reg_out[WORD_SIZE+:WORD_SIZE] ^ reverse_reg_data_out[0+:WORD_SIZE];
    assign state_reg_in_absorb[2] = state_reg_out[2*WORD_SIZE+:WORD_SIZE];
    assign state_reg_in_absorb[3] = state_reg_out[3*WORD_SIZE+:WORD_SIZE];
    assign state_reg_in_absorb[4] = state_reg_out[4*WORD_SIZE+:WORD_SIZE];

    //Inizializzazione dello stato (IV, key1, key2, nonce1, nonce2):
    assign init_data = {
    nonce2,    // 64 bit
    nonce1,             // 64 bit
    key2,             // 64 bit
    key1,          // 64 bit
    initialVector            // 64 bit
    }; // Totale = 320 bit (STATE_WIDTH)

    //Assegnazione del ciphertext:
    assign ciphertext = {state_reg_in_absorb[1], state_reg_in_absorb[0]};

    logic [STATE_WIDTH-1:0] input_state;

    always_comb begin //questo devo modificarlo per ottenere solo 2 MUX a 64 e poi 2 MUX a 320 bit guarda pag 14 Generalizzazione metodo matematico tablet!
        unique case ({sel_absorb_data, sel_init_load})
            2'b10: state_reg_in_shares[0] = {state_reg_in_absorb[4], state_reg_in_absorb[3], state_reg_in_absorb[2], state_reg_in_absorb[1], state_reg_in_absorb[0]};
            2'b01: state_reg_in_shares[0] = init_data;
            2'b00: state_reg_in_shares[0] = input_state;
            //Nota l'xor con la chiave dipende dal rate:
            2'b11: state_reg_in_shares[0] = {state_reg_in_absorb[4], state_reg_in_absorb[3] ^ reg_key2_out, state_reg_in_absorb[2] ^ reg_key1_out, state_reg_in_absorb[1] , state_reg_in_absorb[0]};  
        endcase
    end

    // === Linear diffusion layer ===

    // Parametri di rotazione
    localparam int rotations_a[0:4] = '{19, 61, 1, 10, 7};
    localparam int rotations_b[0:4] = '{28, 39, 6, 17, 41};

    // Funzione di rotazione circolare destra su 64 bit
    function automatic logic [63:0] rotr64(input logic [63:0] x, input int n);
        return (x >> n) | (x << (64 - n));
    endfunction

    // Debug e assegnazione
    logic [63:0] linear_diffusion_debug [0:4];

    //Ora devo ricombinare le shares prima di applicare il layer di diffusione lineare:
    logic [STATE_WIDTH-1:0] recombine_shares;

    //Funzione per l'xor tree: per ricombinare le condivisioni bit a bit
    function automatic logic xor_tree (
        input logic [d:0] in,  // vettore di bit da ridurre
        input int N                      // numero effettivo di bit (uguale a num_shares)
    );
        // Calcola il numero massimo di livelli: serve $clog2(N) + 1
        localparam int MAX_STAGE = $clog2(d+1) + 1;

        // Ogni livello dello XOR tree ha al più num_shares elementi
        logic [(d+1)-1:0] stage [0:MAX_STAGE-1];

        int level = 0;
        int num = N;

        // === Inizializzazione del primo livello con gli input ===
        
        for (int i = 0; i < N; i++) begin
            stage[0][i] = in[i];
        end
        
        // === Costruzione dell'albero XOR ===
        while (num > 1) begin
            // Somma a coppie
            for (int i = 0; i < num / 2; i++) begin
                stage[level + 1][i] = stage[level][2*i] ^ stage[level][2*i + 1];
            end
            // Se numero dispari, porta avanti l'ultimo elemento
            if (num % 2 == 1) begin
                stage[level + 1][num / 2] = stage[level][num - 1];
                num = num / 2 + 1;
            end else begin
                num = num / 2;
            end

            level++;
        end

        // Il risultato finale è il primo elemento dell'ultimo livello
        return stage[level][0];
    endfunction

    // Ricombinazione delle share bit a bit:
    generate
        for (genvar bit_idx = 0; bit_idx < STATE_WIDTH; bit_idx++) begin : recombine
            // Per ogni bit (posizione) ricombina il valore proveniente da tutti i domini (d+1)
            logic [d:0] temp_bits;
            
            always_comb begin
                for (int st_reg = 0; st_reg <= d; st_reg++) begin
                    temp_bits[st_reg] = state_reg_out_shares[st_reg][bit_idx];
                end
                recombine_shares[bit_idx] = xor_tree(temp_bits, d+1);
            end
        end
    endgenerate

    // Applicazione del layer di diffusione lineare:
    generate
        for (genvar i = 0; i < 5; i++) begin : linear_diffusion_layer
            assign linear_diffusion_debug[i] = (sel_masked_round)
                ? recombine_shares[i*64 +: 64]
                    ^ rotr64(recombine_shares[i*64 +: 64], rotations_a[i])
                    ^ rotr64(recombine_shares[i*64 +: 64], rotations_b[i])
                : state_reg_out[i*64 +: 64]
                    ^ rotr64(state_reg_out[i*64 +: 64], rotations_a[i])
                    ^ rotr64(state_reg_out[i*64 +: 64], rotations_b[i]);

            assign linear_diffusion_out[i*64 +: 64] = linear_diffusion_debug[i];
        end
    endgenerate

    //In alcuni casi devo fare l'xor con la chiave per x3 e x4 oppure con 00000...01 solo per x4:
    logic [WORD_SIZE-1:0] mux_linear_diffusion_out_x4;
    logic [WORD_SIZE-1:0] mux_linear_diffusion_out_x3;
    logic [63:0] xor_signal;

   // Linear diffusion layer già calcolato qui sopra
    assign xor_signal = (sel_xor_signal) ? reg_key2_out : {1'b1, {(WORD_SIZE-1){1'b0}}};

    // Output corretto per x4
    assign mux_linear_diffusion_out_x4 = (sel_mux_linear_diffusion_out_x4)
                                        ? (linear_diffusion_debug[4] ^ xor_signal)
                                        : linear_diffusion_debug[4];

    assign mux_linear_diffusion_out_x3 = (sel_mux_linear_diffusion_out_x3)
                                        ? (linear_diffusion_debug[3] ^ reg_key1_out)
                                        : linear_diffusion_debug[3];


    
    assign input_state = {
        mux_linear_diffusion_out_x4,               // MSB
        mux_linear_diffusion_out_x3,
        linear_diffusion_out[2*WORD_SIZE +: WORD_SIZE],
        linear_diffusion_out[1*WORD_SIZE +: WORD_SIZE],
        linear_diffusion_out[0*WORD_SIZE +: WORD_SIZE]  // LSB
    };

    
    //Ora devo gestire l'output del tag:
    assign tag1 = linear_diffusion_out[3*WORD_SIZE+:WORD_SIZE] ^ reg_key1_out;
    assign tag2 = linear_diffusion_out[4*WORD_SIZE+:WORD_SIZE] ^ reg_key2_out;

endmodule

