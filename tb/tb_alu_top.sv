`timescale 1ns/1ps
module tb_alu_top;
    reg clk = 0;
    reg rst_n = 0;
    reg [7:0] a = 0, b = 0;
    reg [2:0] opcode = 0;
    wire [15:0] result;
    reg [15:0] expected, previous;
    integer fd, rc, count = 0, required_count, ia, ib, iop, ie;
    integer per_op [0:7];
    reg [2047:0] vectors, wave;
    alu_top dut (.clk(clk), .rst_n(rst_n), .a(a), .b(b),
                 .opcode(opcode), .result(result));
    always #5 clk = ~clk;
    initial begin
        #20000000; $fatal(1, "Simulation watchdog expired");
    end
    initial begin
        for (integer i=0;i<8;i=i+1) per_op[i]=0;
        if (!$value$plusargs("VECTORS=%s", vectors)) $fatal(1,"Missing VECTORS");
        if (!$value$plusargs("COUNT=%d", required_count)) $fatal(1,"Missing COUNT");
        if ($value$plusargs("VCD=%s", wave)) begin
            $dumpfile(wave); $dumpvars(0, tb_alu_top);
        end
        fd = $fopen(vectors,"r");
        if (!fd) $fatal(1,"Cannot open vectors");
        @(posedge clk); #1;
        if (result !== 16'd0) $fatal(1,"Initial synchronous reset failed");
        previous = result;
        while (!$feof(fd)) begin
            rc = $fscanf(fd,"%d %d %d %d\n",ia,ib,iop,ie);
            if (rc != 4) $fatal(1,"Malformed vector at %0d",count);
            @(negedge clk);
            rst_n=1; a=ia; b=ib; opcode=iop; expected=ie;
            #1;
            if (result !== previous) $fatal(1,"Output changed before rising edge");
            @(posedge clk); #1;
            if ((^result === 1'bx) || result !== expected)
                $fatal(1,"Mismatch #%0d a=%0d b=%0d op=%0d got=%0h expected=%0h",
                       count,a,b,opcode,result,expected);
            previous=result; count=count+1; per_op[iop]=per_op[iop]+1;
            if (count == 100 && wave != 0) $dumpoff;
        end
        $fclose(fd);
        if (count != required_count || count == 0) $fatal(1,"Wrong vector count");
        for (integer i=0;i<8;i=i+1)
            if (per_op[i]==0) $fatal(1,"Uncovered opcode %0d",i);
        // Force a nonzero result, then assert reset strictly between clock edges.
        @(negedge clk); a=255; b=255; opcode=0; rst_n=1;
        @(posedge clk); #1;
        if (result !== 16'd510) $fatal(1,"Pre-reset transaction failed");
        #1; rst_n=0; #1;
        if (result !== 16'd510) $fatal(1,"Reset must be synchronous");
        @(posedge clk); #1;
        if (result !== 0) $fatal(1,"Midstream reset failed");
        @(posedge clk); #1;
        if (result !== 0) $fatal(1,"Reset hold failed");
        @(negedge clk); rst_n=1; a=255; b=1; opcode=1;
        @(posedge clk); #1;
        if (result !== 254) $fatal(1,"Reset release/latency failed");
        $display("PASS vectors=%0d reset_checks=4 latency_checks=%0d",count,count);
        $finish;
    end
endmodule
