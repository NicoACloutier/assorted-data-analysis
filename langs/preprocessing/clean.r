library(tidyverse)

INDO_EUROPEAN <- c("Spanish")
MAYAN <- c("Maya", "Akateko", "Teko", "Chontal", "Chontal de Tabasco", "Jacalteco", "Kekchí", "Tzeltal", "Aguacateco", "Cakchiquel", "Chol", "Chontal de Oaxaca", "Chuj", "Huasteco", "Ixil", "Kanjobal", "Lacandón", "Mame", "Motocintleco", "Quiché", "Tojolabal", "Tzotzil")
UTO_AZTECAN <- c("Guarijío", "Náhuatl", "Pima", "Tepehua", "Tepehuano de Chihuahua", "Yaqui", "Cora", "Huichol", "Mayo", "Pápago", "Tarahumara", "Tepehuano", "Tepehuano de Durango")
OTO_MANGUEAN <- c("Amuzgo", "Chatino", "Chocho", "Ixcateco", "Chinantecas languages", "Zapotecas languages", "Matlatzinca", "Mazahua", "Otomí", "Pame", "Tlapaneco", "Amuzgo de Oaxaca", "Papabuco", "Tacuate", "Chichimeca jonaz", "Cuicateco", "Mixtecas languages", "Mazateco", "Ocuilteco", "Popoloca", "Popoluca de la Sierra", "Popoluca de Texistepec", "Triqui", "Amuzgo de Guerrero", "Solteco")
YUMAN_COCHIMI <- c("Cochimí", "Cucapá", "Kiliwa", "Paipai", "Kumiai")
HUAVE <- c("Huave")
MIXE_ZOQUEAN <- c("Mixe", "Popoluca", "Popoluca de Oluta", "Ayapaneco", "Sayulteco", "Zoque")
PUREPECHA <- c("Purépecha")
SERI <- c("Seri")
TOTONACAN <- c("Totonaca")
ALGONQUIN <- c("Kikapú")

get_family <- function(language_name) {
    if (language_name %in% INDO_EUROPEAN) { return("Indo-European") } 
    else if (language_name %in% MAYAN) { return("Mayan") }
    else if (language_name %in% UTO_AZTECAN) { return("Uto-Aztecan") }
    else if (language_name %in% OTO_MANGUEAN) { return("Oto-Manguean") }
    else if (language_name %in% YUMAN_COCHIMI) { return("Yuman-Cochimí") }
    else if (language_name %in% HUAVE) { return("Huave") }
    else if (language_name %in% MIXE_ZOQUEAN) { return("Mixe-Zoquean") }
    else if (language_name %in% PUREPECHA) { return("Purépecha") }
    else if (language_name %in% SERI) { return("Seri") }
    else if (language_name %in% TOTONACAN) { return("Totonacan") }
    else if (language_name %in% ALGONQUIN) { return("Algonquin") }
    return("None")
}

langs <- read.csv("../data/raw/data.csv") %>%
    select(year, area, sex, language, value) %>%
    filter(!(language %in% c("Other native languages of America", "Other native languages non specified", 
                             "Other native languages of Mexico", "Native", "Not stated", "Spanish and native language", "Total"))) %>%
    mutate(family = map(language, get_family)) %>%
    mutate(family = unlist(family)) %>%
    unite(group, area:sex, sep="-") %>%
    spread(group, value) %>%
    mutate(population_order = round(log10(`Total-Both Sexes`))) %>%
    group_by(language) %>%
    mutate(max_order = max(population_order))

write.csv(langs, "../data/cleaned/langs.csv", row.names = FALSE)