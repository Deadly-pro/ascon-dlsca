// ============================================================================
// Module: shareCreator
// Descrizione:
//   Questo modulo genera le condivisioni (shares) mascherate di un dato input
//   secondo uno schema di mascheramento a d-ordine (utilizzando d maschere 
//   casuali), producendo in totale (d+1) shares.
//
//   L'output è formato dalle d maschere casuali più una share "corretta" 
//   calcolata come XOR tra il dato originale e tutte le maschere. Questo schema
//   garantisce che la somma XOR di tutte le shares restituisca il dato originale.
//
//   Le shares sono ordinate in uscita come segue:
//     - Le condivisioni sono raggruppate per dominio (es. A, B, C) a blocchi di
//       COL_SIZE*PAR bit ciascuna.
//     - L'ordine è: 
//         [dominio_C][dominio_B]...[dominio_A]
//       cioè dalla maschera più recente (random_masks[d-1]) fino alla "corretta"
//       (XOR finale), con:
//         shares_out = {x_COL_C, x_COL_B, ..., x_COL_A}
//
//   Ad esempio, con d = 2 e COL_SIZE = 5:
//     - `shares_out[14:10]` contiene x4_C, ..., x0_C (dominio C),
//     - `shares_out[9:5]`   contiene x4_B, ..., x0_B (dominio B),
//     - `shares_out[4:0]`   contiene x4_A, ..., x0_A (dominio A/corretta).
//
//   Parametri:
//     - d: ordine del mascheramento (es. 2 implica 3 shares),
//     - COL_SIZE: dimensione di un blocco di dati (es. 5 bit),
//     - PAR: parallelismo (numero di blocchi elaborati in parallelo).
//
//   Utilizzato tipicamente come fase iniziale nel mascheramento di dati sensibili.
// ============================================================================
import ascon_params::PAR;
import ascon_params::d;
import ascon_params::COL_SIZE;

module shareCreator 
(
    input  logic [COL_SIZE*PAR-1:0] data_in,
    input  logic [d*COL_SIZE*PAR-1:0] random_masks,  // d maschere
    output logic [(d+1)*COL_SIZE*PAR-1:0] shares_out // (d+1) shares
);
    //Il blocco da in uscita {shares A[4:0], shares B[9:5], shares C}
    logic [COL_SIZE*PAR-1:0] temp;
    always_comb begin
        temp = data_in;
        for (int i = 0; i < d; i++) begin
            shares_out[(i+1)*COL_SIZE*PAR +: COL_SIZE*PAR] = random_masks[i*COL_SIZE*PAR +: COL_SIZE*PAR];
            temp ^= random_masks[i*COL_SIZE*PAR +: COL_SIZE*PAR];
        end
        shares_out[0 +: COL_SIZE*PAR] = temp;
    end
endmodule
