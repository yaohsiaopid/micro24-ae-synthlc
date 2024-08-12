# RTL2MμPATH – DUV PLs derivation and DFG Analysis 
We first introduce the components of RTL2MμPATH shared across all instruction-under-verifications (IUV). That is, the DUV PLs (§V-B1) and the candidate happens-before edges derived from the design DFG as explained in §V-B5. 

## DUV PL enumeration

`$ cd fv; ./run_duvpls.sh` 

The scripts does the followings:   
a. Enunmerates PLs based on the (PCR, uFSMs) annotation and width of the uFSMS in
  `annotation_pcr_ufsms.txt` and evaluate the reachability for DUV (§V-B1).
b. Output a set of DUV PLs in `xDUVPLs/reachable_duvpls.sv`. One will see the 
```
wire serdiv_unit_divide_s1 = ...
...
wire serdiv_unit_divide_s2 = ...
```
Each wire is a PL correspond to the row labels for a μpath. As an example, the wire `issue_s8`/`lsq_enq_0_s1` corresponds to the `issue`/`LSQ` stage in the Fig. 2 of the paper. 
There will be a total of 40 wires that correspond to 40 DUV PLs on the CVA6. Along with the PL corresponding to IF, we have a total of 41 DUV PLs just as reported in our paper §V-B1. 


## DFG generation 

`$ cd fv; ./run_gendfg.sh`

The DFG generation will be used in Happens-Before Edge evaluation in §V-B5. 
Specifically, we only consider candidate HB edges all ordered pairs of PLs that are connected via pure combinational logic in the DUV to capture exclusively causal happens-before relationship among visited PLs.

Since this step can take 40min to 1h depending on number of DUV PLs, we bypass this with a pre-loaded file.
If one wnats to re-produce the file, use `$ cd fv; BYPASS=0 ./run_gendfg.sh` (optional, as the remaining flow will take much longer time). 


