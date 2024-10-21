library(tidyverse)
library(lubridate)
library(dplyr)
source("https://raw.githubusercontent.com/marshalln7/ADNI/refs/heads/main/Dallan%20Work/calc.visit.dx.R")

registry <- read.csv("https://raw.githubusercontent.com/marshalln7/ADNI/refs/heads/main/Datasets/Raw%20Data%20Files/REGISTRY%20-%20Registry%20%5BADNI1%2CGO%2C2%2C3%5D.csv")
dxsum <- read.csv("https://raw.githubusercontent.com/marshalln7/ADNI/refs/heads/main/Datasets/Raw%20Data%20Files/PDXCONV%20DXSUM%20-%20Diagnostic%20Summary%20%5BADNI1%2CGO%2C2%2C3%2C4%5D.csv")

visit.diagnosis <- calc.visit.dx(registry, dxsum)
write_csv(visit.diagnosis, "C:/School/RA Work/ADNI/Dallan Work/visit_dx_combined.csv")