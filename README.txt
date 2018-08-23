'MetaVars.py' defines Python classes for "describing" an ordered list of variables.

Refer by way of example to: 'inputspec.xml'

This example xml "describes" 19 variables. Let's look at a couple of these variables by way of example:

---

<direction type='bool'>0</direction>

The variable name is: 'direction' (required).
Its type is: boolean (required).
Its default value is: 0/false (optional).

---

<fileIdx type='int' min='5' max='500'>53</fileIdx>

The variable name is: 'fileIdx' (required).
Its type is: integer (required).
Its default value is: 53 (optional).
Its min value is: 5 (optional).
Its max value is: 500 (optional).

---

OK consider what 'Driver1.py' (tester 1) is doing.

We run it like this by way of example:

$ python Driver1.py -i inputspec.xml -o test.txt -n 20 -s 5000

Tester 1 takes in a variables "description" file: 'inputspec.xml'.
It generates real values for the described variables and outputs these values to: 'test.txt'.
Consider the first line in 'test.txt':

1166 1 2276 2508 4198 504957743 343181948 520947406 1 0 2444 3288 2919 0 1 4366 3473 1492 adbfce05bcb4e0dc0747ea054e2151b9df56a57e

19 randomly generated (based on the input seed value 5000) variable values are specified. 
These values pertain (in order) to the 19 variables specified in 'inputspec.xml':

1166     <- TBS
1        <- SRS
2276     <- cellId
...
etc.

There are 20 lines in 'test.txt', corresponding to the '-n 20' argument. This is instructing tester 1
to generate 20 instantiations of the meta-variables set.

---

<CellID type="bin">

  <RNTI type="bin">
    <full_sample_idx type="sort"></full_sample_idx>
    <file_sample_idx type="sort"></file_sample_idx>
  </RNTI>

  <prb_offset type="bin">
    <N_PRB type="bin">
      <full_sample_idx type="sort"></full_sample_idx>
      <file_sample_idx type="sort"></file_sample_idx>
    </N_PRB>
  </prb_offset>

  <TBS type="bin">
    <prb_offset type="bin">
      <N_PRB type="bin">
        <full_sample_idx type="sort"></full_sample_idx>
        <file_sample_idx type="sort"></file_sample_idx>
      </N_PRB>
    </prb_offset>
  </TBS>

</CellID>

What is this telling us to do?
First divide CellId into "bins". So you have to suppose there are metavar sets with the same CellID var value.
Create directories for each:

CellID_5
CellID_10
CellId_20
etc.

Within each of these dirs, create separate bins again for RNTI, prb_offset, and TBS.

CellID_5
|-RNTI_27
|-RNTI_86
|-...
|-prb_offset_8
|-prb_offset_12
|-...
|-TBS_32
|-TBS_33
|-...
CellID_10
|-RNTI_27
|-RNTI_86
|-...
|-prb_offset_8
|-prb_offset_12
|-...
|-TBS_32
|-TBS_33
|-...
CellId_20
|-RNTI_27
|-RNTI_86
|-...
|-prb_offset_8
|-prb_offset_12
|-...
|-TBS_32
|-TBS_33
|-...

Then within each of these dirs, create sub dirs where you sort on full_sample_idx and file_sample_idx:

CellID_5
|-RNTI_27
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-RNTI_86
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
|-prb_offset_8
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-prb_offset_12
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
|-TBS_32
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-TBS_33
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
CellID_10
|-RNTI_27
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-RNTI_86
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
|-prb_offset_8
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-prb_offset_12
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
|-TBS_32
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-TBS_33
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
CellId_20
|-RNTI_27
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-RNTI_86
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
|-prb_offset_8
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-prb_offset_12
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...
|-TBS_32
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-TBS_33
|   |-full_sample_idx_sort
|   |-file_sample_idx_sort
|-...













