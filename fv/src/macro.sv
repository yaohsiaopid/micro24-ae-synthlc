property CONST (N);
    @(posedge clk_i) N == $past(N);
endproperty
`define STORE 7'b0100011
`define LOAD 7'b0000011

reg first;
`ifdef SYMSTART
wire rst_ni_psuedo;
`endif
always @(posedge clk_i) begin
`ifdef SYMSTART
    if (!rst_ni_psuedo) begin
`else
    if (!rst_ni) begin
`endif
        first <= 1;
    end else if (first == 1) begin
        first <= 0;
    end 
end

