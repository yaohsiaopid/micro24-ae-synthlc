# Design Annotation and Environment Setup
This part will walk through the annotation preparation for CVA6 and formal environment setup for properties evaluation. 

## Directory structure
We use `$REPO` to refer to the path of the repository (`$ export REPO=<synthlc-path>`). 

  - `$REPO/cva6`: 
    - Source: https://github.com/openhwgroup/cva6 at commit `#00236be`
    - Added behavior model of memory and made modification primarily in `core/{load_store_unit, store_buffer}.sv` for `CVA6 Core` evaluation in §VI such that load-store unit and committed STB are directly interfaced with the memory.
   - `$REPO/fv`: include formal environment, rtl2mupath and SynthLC code base.  

## Flow
1. Formal environment setup.  

    a. Identify IIR and μFSMs, and augment PCRs for non-PCR IIRs as in §V-A and Table II in the paper. 
    -  `$ grep -IR "for FVT" cva6/core/* 2>/dev/null >> diff_for_fv.log && wc -l diff_for_fv.log`
        lists all 39 lines of modification as in Table II.

    b. Prepare all tuples of (PCR, uFSMs) as in `fv/annotation_pcr_ufsms.txt`
    - `$ grep "pc" fv/annotation_pcr_ufsms.txt`   
      The command should return 20. Along with
      the PCR at the IF stage (as in `$REPO/fv/src/header_fv.sv:52`), we have a total of
      21 PCRs as in the Table II. 

    c. The header `fv/src/header_fv.sv` sets up the formal environment for CVA6, including assumptions on signals outputted from frontend, which is black-boexed, and the instruction-under-verification (IUV) that is symbolically driven at IFR with the ufsm at IF stage being valid shown in line 52 with `wire instn_begin` (§V-A). 

2. Scripts setup and test.
  From the top directory `$REPO`: 

    a. `$ cd fv; ./setup_scripts.sh`

    b. `$ cd synthlc; . ./env.sh; cd ../`  
    Sets the clock and reset signal name. 

    c. At `fv`:   
    `$ mkdir xSanity; touch xSanity/xSanity.sv; ./RUN_JG.sh -j xSanity -s xSanity/xSanity.sv -g 0`.  
    If things are set up correctly, it should returns a success ending with the following: 
    ```
    ....
    [mytask] % INFO (IPL005): Received request to exit from the console.
    INFO (IPL014): Waiting for the Tcl-thread to exit.
    INFO: Waiting for proof threads to stop...
    INFO: Proof threads stopped.
    INFO (IPL018): The peak resident set memory use for this session was 0.414 GB.
    INFO (IPL015): The Tcl-thread exited with status 0.
    INFO (IPL016): Exiting the analysis session with status 0.
    ```

3. **Important Note for Property Evaluation**:  
Configure the maximum number of JasperGold jobs that can be run concurrently. This depends on the nubmer of cores and the size of memory of one's machine. 
As mentioned in the artifact section of the paper, the execution time is collected on a machine with 128 cores and 700GB memory and configured with `NNN=3`. 
If one's machine has only 48-64 cores or less, we recommend running below commands to set the environment variable:
`$ export NNN=<3/2/1>`.  
This step may slightly impact the property evaluation result, turning ones reported covered into undetermined and causing slight difference from the expected output. 