`timescale 1ns/1ps
// Synchronous active-low reset. Inputs are sampled at each rising clock edge.
module alu_top (
    input logic clk, rst_n,
    input logic [7:0] a, b,
    input logic [2:0] opcode,
    output logic [15:0] result
);
    wire [15:0] combinational_result;
    alu_8bit core (.a(a), .b(b), .opcode(opcode), .result(combinational_result));
    always_ff @(posedge clk) begin
        if (!rst_n) result <= 16'd0;
        else result <= combinational_result;
    end
endmodule
