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

#Checking for multicollinearity
cor(np)
correlation_matrix <- cor(np)
#For now, I am setting the multicollinearity threshold at .5.  Combinations that do not meet this restriction:
  #Cerebral_cortex_atrophy & Hippocampus_atrophy
  #Thal_phase_IHC & Braak_stage_neurofib_degen
  #Thal_phase_IHC & CERAD_score_neuritic
  #Thal_phase_IHC & NIAA_AA_ADNC
  #Thal_phase_IHC & CERAD_score_diffuse
  #Thal_phase_IHC & Cerebral_amyloid_angiopathy
  #Braak_stage_neurofib_degen & CERAD_score_neuritic
  #Braak_stage_neurofib_degen & NIAA_AA_ADNC
  #Braak_stage_neurofib_degen & CERAD_score_diffuse
  #CERAD_score_neuritic & NIAA_AA_ADNC
  #CERAD_score_neuritic & CERAD_score_diffuse
  #NIAA_AA_ADNC & CERAD_score_diffuse

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


#here's a function that creates the model and does the assumption checks if you jsut give it the formula
regression_function <- function(formula){
  wbw1 = lm(formula, data = np)
  print(summary(wbw1))
  #Checking Assumptions
  print(r.squaredGLMM(wbw1))
  print(par(mfrow = c(2,2), oma = c(0,0,2,0)))
  hist(residuals(wbw1))
  qqnorm(residuals(wbw1))
  plot(residuals(wbw1))
  plot(cooks.distance(wbw1))
}

#here's how you call it, you just give it the formula
regression_function(Whole_brain_weight ~ Cerebral_cortex_atrophy + Tau_antibody + TDP43_antibody + Thal_phase_IHC + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis)


#Regressions
wbw1 = lm(Whole_brain_weight ~ Cerebral_cortex_atrophy + Tau_antibody + TDP43_antibody + Thal_phase_IHC + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw1)
  #Checking Assumptions
r.squaredGLMM(wbw1)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw1))
qqnorm(residuals(wbw1))
plot(residuals(wbw1))
plot(cooks.distance(wbw1))

wbw2 = lm(Whole_brain_weight ~ Hippocampus_atrophy + Tau_antibody + TDP43_antibody + Thal_phase_IHC + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw2)
  #Checking Assumptions
r.squaredGLMM(wbw2)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw2))
qqnorm(residuals(wbw2))
plot(residuals(wbw2))
plot(cooks.distance(wbw2))

wbw3 = lm(Whole_brain_weight ~ Cerebral_cortex_atrophy + Tau_antibody + TDP43_antibody + Braak_stage_neurofib_degen + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw3)
  #Checking Assumptions
r.squaredGLMM(wbw3)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw3))
qqnorm(residuals(wbw3))
plot(residuals(wbw3))
plot(cooks.distance(wbw3))

wbw4 = lm(Whole_brain_weight ~ Hippocampus_atrophy + Tau_antibody + TDP43_antibody + Braak_stage_neurofib_degen + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw4)
  #Checking Assumptions
r.squaredGLMM(wbw4)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw4))
qqnorm(residuals(wbw4))
plot(residuals(wbw4))
plot(cooks.distance(wbw4))

wbw5 = lm(Whole_brain_weight ~ Cerebral_cortex_atrophy + Tau_antibody + TDP43_antibody + CERAD_score_neuritic + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_Sclerosis, data = np)
summary(wbw5)
  #Checking Assumptions
r.squaredGLMM(wbw5)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw5))
qqnorm(residuals(wbw5))
plot(residuals(wbw5))
plot(cooks.distance(wbw5))

wbw6 = lm(Whole_brain_weight ~ Hippocampus_atrophy + Tau_antibody + TDP43_antibody + CERAD_score_neuritic + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw6)
  #Checking Assumptions
r.squaredGLMM(wbw6)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw6))
qqnorm(residuals(wbw6))
plot(residuals(wbw6))
plot(cooks.distance(wbw6))

wbw7 = lm(Whole_brain_weight ~ Cerebral_cortex_atrophy + Tau_antibody + TDP43_antibody + CERAD_score_diffuse + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw7)
  #Checking Assumptions
r.squaredGLMM(wbw7)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw7))
qqnorm(residuals(wbw7))
plot(residuals(wbw7))
plot(cooks.distance(wbw7))

wbw8 = lm(Whole_brain_weight ~ Hippocampus_atrophy + Tau_antibody + TDP43_antibody + CERAD+score_diffuse + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(wbw8)
  #Checking Assumptions
r.squaredGLMM(wbw8)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(wbw8))
qqnorm(residuals(wbw8))
plot(residuals(wbw8))
plot(cooks.distance(wbw8))
#These models don't include the NIAA_AA_ADNC variable since we are using it as a Response Variable.  Should that be so?

nia1 = lm(NIAA_AA_ADNC ~ Cerebral_cortex_atrophy + Tau_antibody + TDP43_antibody + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(nia1)
  #Checking Assumptions
r.squaredGLMM(nia1)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(nia1))
qqnorm(residuals(nia1))
plot(residuals(nia1))
plot(cooks.distance(nia1))

nia2 = lm(NIAA_AA_ADNC ~ Hippocampus_atrophy + Tau_antibody + TDP43_antibody + Cerebral_amyloid_angiopathy + Arteriolosclerosis + Hippocampal_sclerosis, data = np)
summary(nia2)
  #Checking Assumptions
r.squaredGLMM(nia2)
par(mfrow = c(2,2), oma = c(0,0,2,0))
hist(residuals(nia2))
qqnorm(residuals(nia2))
plot(residuals(nia2))
plot(cooks.distance(nia2))
#These models don't include the Whole_brain_weight variable since we are using it as a Response Variable. Should that be so?

#Variables of interest
  #Response Variables: NIA-AA Alzheimer's Disease Neuropathologic change & Whole Brain Weight
  #Explanatory Variables: Whole Brain Weight; Cerebral Cortex Atrophy; Hippocampus Atrophy; Thal phase for amyloid plaques by immunohisto-chemistry (IHC)
    #Braakk stage for neurofibrillary degeneration; Cerad score for density of neocortical neuritic plaque; CERAD semi-quantitative score for diffuse plaques; 
    #Cerebral amyloid angiopathy; arteriolosclerosis; Hippocampal sclerosis; antibodies against amyloid, tau, and alpha synuclein
  #The NIA-AA variable is calculated using the "Thal phase for amyloid plaques by immunohistochemistry (IHC) variable, the Braak stage for neurofibrillary degeneration variable, and the CERAD score for density of neocortical neuritic plaque (plaques with argyrophilic dystrophic neurites, with or without dense amyloid cores)
