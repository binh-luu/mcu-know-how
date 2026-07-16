#include <stdio.h>

typedef signed char    sint8;
typedef unsigned char  uint8;
typedef signed short   sint16;
typedef unsigned short uint16;
typedef signed long    sint32;
typedef unsigned long  uint32;

#define N 10

typedef struct {
    sint16 temperature;
    uint32 Setdata;
} VariableA;

VariableA TableData[N];

/* Finds the index of the first table entry whose temperature is >= the
   current temperature, so [idx-1, idx] brackets pcurData->temperature. */
static uint16 findIndex(sint16 currentTemp, const VariableA* pTableData)
{
    uint16 idx;
    for (idx = 1U; idx < (uint16)(N - 1); idx++)
    {
        if (currentTemp <= pTableData[idx].temperature)
        {
            break;
        }
    }
    return idx;
}

static uint16 linearinterpolation(const VariableA *pcurData, const VariableA* pTableData)
{   /* Declare local variables */
    sint32 deltaOut;
    sint32 deltaIn;
    uint16 output;
    uint16 idx;

    /* Find the bracketing index for the current temperature. */
    idx = findIndex(pcurData->temperature, pTableData);

    /* DeltaIn of temperatures. */
    deltaIn = (sint32)(pTableData[idx].temperature) - (sint32)(pTableData[idx-1].temperature);
    /* DeltaOut of Setdata */
    deltaOut = (sint32)pTableData[idx].Setdata - (sint32)pTableData[idx-1].Setdata;

    /* Division by 0 protection. */
    if (deltaIn == 0)
    {   /* if the division == 0 */
        output = (uint16)pTableData[idx-1].Setdata;
    }
    else
    {   /* MISRA C:2012 Rule 10.8 */
        output = (uint16)((((deltaOut * 1000) / deltaIn) *
                    ((sint32)(pcurData->temperature) - (sint32)(pTableData[idx-1].temperature)) / 1000)
                    + (sint32)pTableData[idx-1].Setdata);
    }
    return output;
}

int main(void)
{
    uint16 i;
    VariableA curData;
    uint16 result;

    /* Populate the lookup table with dummy calibration data:
       temperature rises in steps of 10, Setdata rises in steps of 100. */
    for (i = 0U; i < N; i++)
    {
        TableData[i].temperature = (sint16)(i * 10);
        TableData[i].Setdata     = (uint32)(i * 100);
    }

    /* Simulate calling linearinterpolation() with a dummy current reading. */
    curData.temperature = 25;   /* falls between TableData[2] (20) and TableData[3] (30) */
    curData.Setdata      = 0;    /* unused by the function, just for struct completeness */

    result = linearinterpolation(&curData, TableData);

    printf("Current temperature: %d\n", curData.temperature);
    printf("Interpolated Setdata output: %u\n", result);

    return 0;
}
