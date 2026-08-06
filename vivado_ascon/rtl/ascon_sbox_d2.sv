// ============================================================================
// Module: ascon_sbox_d2
// Descrizione:
//   Questo modulo implementa la S-box dell'algoritmo ASCON in una versione 
//   sicura contro attacchi side-channel, usando tecniche di mascheramento a 
//   d+1 condivisioni (shares).
//
//   In particolare, realizza una S-box a 5 bit con mascheramento d'ordine d,
//   sfruttando la tecnica DOM (Domain-Oriented Masking) per proteggere le 
//   operazioni AND. Il modulo include:
//     - La computazione combinatoria della funzione S-box mascherata,
//     - L'uso di randomness fresca per ogni DOM-AND,
//     - La registrazione dei risultati per garantire la sicurezza contro glitch,
//     - L'output sia mascherato che non mascherato (per debug o verifica).
//
//   Parametri:
//     - d: ordine di mascheramento (es. 1 = 2 shares),
//     - num_shares: numero di condivisioni (tipicamente d+1).
//
// ============================================================================
import ascon_params::d;
import ascon_params::num_shares;

module ascon_sbox_d2 (
    input  logic clk,
    input  logic [((d+1)*5)-1:0] x_in, // 5 bit × (d+1) share
    input  logic [((d+1)*(d)/2)-1:0] fresh_r, // 3 bit di fresh per ogni AND
    input logic sel_masked_round, // selettore per mascheramento
    output logic [((d+1)*5)-1:0] x_out,
    output logic [((d+1)*5)-1:0] x_out_noMask
);

    // Unpack input
    logic [(d+1)-1:0] x[0:4];
    assign {x[4], x[3], x[2], x[1], x[0]} = x_in;

    // Buffer per ogni DOM-AND (5 bit → 5 blocchi DOM-AND)
    logic [(d+1)-1:0][(d+1)-1:0] and_result_bank[0:4]; // combinatorial
    logic [(d+1)-1:0][(d+1)-1:0] and_result_reg [0:4]; // registered
    logic [(d+1)-1:0] y[0:4]; // final output per bit
    logic [num_shares-1:0] y_noMask[0:4];     // output non mascherato (diagonali)

    // === Fase 1: Calcolo DOM-AND combinatoriale ===
    always_comb begin
        int fresh_idx;
        
        for (int i = 0; i < 5; i++) begin
            //questi segnali prima erano con anche "logic [(d+1)-1:] xi [0:4] ma in sintesi dava problemi:
            logic [(d+1)-1:0] xi;
            logic [(d+1)-1:0] xiprox1;
            logic [(d+1)-1:0] xiprox2;
            logic [(d+1)-1:0] not_xiprox1; // Negazione della prima share

            xi        = x[i]; //xi contiene xi con tutti i bit delle shares
            xiprox1   = x[(i+1)%5];
            xiprox2   = x[(i+2)%5];
            //logic [(d+1)-1:0] not_xiprox1 = ~xiprox1;
            
            if (( d % 2 == 1 ) && (sel_masked_round == 1)) begin
                // Se d è pari, non nego la prima share
                not_xiprox1 = xiprox1;
                not_xiprox1[0] = ~xiprox1[0]; // Nego solo la prima share, questo si fa perchè se ho un numero di share pari e come non effettuare la negazione!
            end else begin
                // Se d è dispari, nego la prima share
                not_xiprox1 = ~xiprox1;
            end
              
            
            // reset del risultato
            and_result_bank[i] = '{default: 0};
            fresh_idx = 0;
            for (int j = 0; j < (d+1); j++) begin //cicla sui domini A,B e C etc.
                for (int k = 0; k < (d+1); k++) begin //cicla sulla and di ogni dominio
                    if (j == k) begin
                        and_result_bank[i][j][k] = (not_xiprox1[j] & xiprox2[k]) ^ xi[j];
                        y_noMask[i][j] = and_result_bank[i][j][k]; // output non mascherato
                    end else if (j < k) begin
                        and_result_bank[i][j][k] = not_xiprox1[j] & xiprox2[k] ^ fresh_r[fresh_idx];
                        and_result_bank[i][k][j] = not_xiprox1[k] & xiprox2[j] ^ fresh_r[fresh_idx];
                        fresh_idx++;
                    end
                end
            end
        end
    end

    // === Fase 2: stadio di FF per ottenere glitch-security ===
    always_ff @(posedge clk) begin
        for (int i = 0; i < 5; i++) begin
            and_result_reg[i] <= and_result_bank[i];
        end
    end

    //Funzione per l'xor tree:
    function automatic logic xor_tree (
        input logic [num_shares-1:0] in,  // vettore di bit da ridurre
        input int N                      // numero effettivo di bit (uguale a num_shares)
    );
    // Calcola il numero massimo di livelli: serve $clog2(N) + 1
    localparam int MAX_STAGE = $clog2(num_shares) + 1;

    // Ogni livello dello XOR tree ha al più num_shares elementi
    logic [num_shares-1:0] stage [0:MAX_STAGE-1];

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



always_comb begin
    for (int i = 0; i < 5; i++) begin
        for (int j = 0; j < num_shares; j++) begin
            logic [num_shares-1:0] temp;
            for (int k = 0; k < num_shares; k++) begin
                temp[k] = and_result_reg[i][j][k];
            end
            y[i][j] = xor_tree(temp, num_shares);
        end
    end
end

assign x_out = {y[4], y[3], y[2], y[1], y[0]};
assign x_out_noMask  = {y_noMask[4], y_noMask[3], y_noMask[2], y_noMask[1], y_noMask[0]};
endmodule
