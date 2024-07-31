####Regression Analysis for the Neuropathology Data####
#Getting the right packages
library(MuMIn)
#install.packages("janitor")
library(janitor)

#Accessing the data
getwd()
neuropath <- read.csv("NEUROPATH - NACC Neuropathology Data Form [ADNI1,GO,2,3].csv")
colnames(neuropath)
#neuropath <- janitor::row_to_names(neuropath, 1, remove_row = TRUE)
help("row_to_names")

#Renaming Variables of Interest
names(neuropath) [4] <- "Date Form Completed - Month"
names(neuropath)[1] <- "Line_Number"
names(neuropath) [12] <- "Whole_brain_weight"
names(neuropath) [14] <- "Cerebral_cortex_atrophy"
names(neuropath) [16] <- "Hippocampus_atrophy"
names(neuropath) [20] <- "Tau_antibody"
names(neuropath) [22] <- "Amyloid_beta_antibody"
  #This variable is only 2 on everyone, so I am withholding it from the analysis for now.
names(neuropath) [24] <- "Alpha_synuclein_antibody"
names(neuropath) [26] <- "TDP43_antibody"
names(neuropath) [34] <- "Thal_phase_IHC"
names(neuropath) [35] <- "Braak_stage_neurofib_degen"
names(neuropath) [36] <- "CERAD_score_neuritic"
names(neuropath) [37] <- "NIAA_AA_ADNC"
names(neuropath) [38] <- "CERAD_score_diffuse"
names(neuropath) [39] <- "Cerebral_amyloid_angiopathy"
names(neuropath) [71] <- "Arteriolosclerosis"
names(neuropath) [89] <- "Hippocampal_sclerosis"
colnames(neuropath)

#Subset dataframe just with the Variables of Interest
np <- subset(neuropath, select = c(Whole_brain_weight, Cerebral_cortex_atrophy, Hippocampus_atrophy, Tau_antibody, Amyloid_beta_antibody, Alpha_synuclein_antibody, TDP43_antibody, Thal_phase_IHC, Braak_stage_neurofib_degen, CERAD_score_neuritic, NIAA_AA_ADNC, CERAD_score_diffuse, Cerebral_amyloid_angiopathy, Arteriolosclerosis, Hippocampal_sclerosis))
#np <- np[-c(1, 2), ]
str(np)
np$Whole_brain_weight = as.numeric(np$Whole_brain_weight)
np$Cerebral_cortex_atrophy = as.factor(np$Cerebral_cortex_atrophy)
np$Hippocampus_atrophy = as.factor(np$Hippocampus_atrophy)
np$Tau_antibody = as.factor(np$Tau_antibody)
np$Amyloid_beta_antibody = as.factor(np$Amyloid_beta_antibody)
np$Alpha_synuclein_antibody = as.factor(np$Alpha_synuclein_antibody)
np$TDP43_antibody = as.factor(np$TDP43_antibody)
np$Thal_phase_IHC = as.factor(np$Thal_phase_IHC)
np$Braak_stage_neurofib_degen = as.factor(np$Braak_stage_neurofib_degen)
np$CERAD_score_neuritic = as.factor(np$CERAD_score_neuritic)
np$NIAA_AA_ADNC = as.factor(np$NIAA_AA_ADNC)
np$CERAD_score_diffuse = as.factor(np$CERAD_score_diffuse)
np$Cerebral_amyloid_angiopathy = as.factor(np$Cerebral_amyloid_angiopathy)
np$Arteriolosclerosis = as.factor(np$Arteriolosclerosis)
np$Hippocampal_sclerosis = as.factor(np$Hippocampal_sclerosis)
str(np)

#ANOVA
wbw_aov = aov(Whole_brain_weight ~ Tau_antibody + Alpha_synuclein_antibody + TDP43_antibody + Thal_phase_IHC + Braak_stage_neurofib_degen + CERAD_score_neuritic + NIAA_AA_ADNC + CERAD_score_diffuse + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw_aov)
TukeyHSD(wbw_aov)


#This model is throwing errors and I'm not sure how to fix it.
nia_aov = aov(NIAA_AA_ADNC ~ Whole_brain_weight + Cerebral_cortex_atrophy + Hippocampus_atrophy + Tau_antibody + Alpha_synuclein_antibody + TDP43_antibody + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(nia_aov)


#Variables of interest
  #Response Variables: NIA-AA Alzheimer's Disease Neuropathologic change & Whole Brain Weight
  #Explanatory Variables: Whole Brain Weight; Cerebral Cortex Atrophy; Hippocampus Atrophy; Thal phase for amyloid plaques by immunohisto-chemistry (IHC)
    #Braakk stage for neurofibrillary degeneration; Cerad score for density of neocortical neuritic plaque; CERAD semi-quantitative score for diffuse plaques; 
    #Cerebral amyloid angiopathy; arteriolosclerosis; Hippocampal sclerosis; antibodies against amyloid, tau, and alpha synuclein
  #The NIA-AA variable is calculated using the "Thal phase for amyloid plaques by immunohistochemistry (IHC) variable, the Braak stage for neurofibrillary degeneration variable, and the CERAD score for density of neocortical neuritic plaque (plaques with argyrophilic dystrophic neurites, with or without dense amyloid cores)
