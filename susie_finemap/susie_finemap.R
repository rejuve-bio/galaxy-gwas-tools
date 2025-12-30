# #!/usr/bin/env Rscript

# suppressMessages(library(optparse))
# suppressMessages(library(susieR))

# # Define arguments
# option_list <- list(
#   make_option("--sumstats", type="character", help="GWAS summary stats file (tabular)"),
#   make_option("--ld_matrix", type="character", help="LD matrix file (tabular)"),
#   make_option("--snp_list", type="character", help="SNP list file (tabular)"),
#   make_option("--L", type="integer", default=-1, help="Number of components (default=-1 auto)"),
#   make_option("--coverage", type="double", default=0.95, help="Credible set coverage (default=0.95)"),
#   make_option("--n", type="integer", help="Sample size (required)"),
#   make_option("--credible_sets_out", type="character", help="Output file for credible sets"),
#   make_option("--pips_out", type="character", help="Output file for SNPs with PIPs")
# )

# opt <- parse_args(OptionParser(option_list=option_list))

# # Read inputs
# sumstats <- read.table(opt$sumstats, header=TRUE)
# ld <- as.matrix(read.table(opt$ld_matrix, header=FALSE))
# snps <- read.table(opt$snp_list, header=FALSE, stringsAsFactors=FALSE)[,1]

# # Expect summary stats with columns: SNP, BETA, SE
# if(!all(c("SNP","BETA","SE") %in% colnames(sumstats))){
#   stop("Summary stats must contain columns: SNP, BETA, SE")
# }

# # Match SNP order
# common_snps <- intersect(snps, sumstats$SNP)
# sumstats <- sumstats[match(common_snps, sumstats$SNP),]
# ld <- ld[match(common_snps, snps), match(common_snps, snps)]

# # Run SuSiE
# L <- ifelse(opt$L == -1, 10, opt$L)
# res <- susie_rss(bhat = sumstats$BETA,
#                  shat = sumstats$SE,
#                  R = ld,
#                  n = opt$n,
#                  L = L,
#                  coverage = opt$coverage)

# # Write credible sets
# cred_sets <- susie_get_cs(res, coverage = opt$coverage)
# write.table(cred_sets$cs, file=opt$credible_sets_out,
#             sep="\t", quote=FALSE, row.names=FALSE, col.names=TRUE)

# # Write PIPs
# pips <- data.frame(SNP=common_snps, PIP=res$pip)
# write.table(pips, file=opt$pips_out,
#             sep="\t", quote=FALSE, row.names=FALSE, col.names=TRUE)





#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(optparse)
  library(susieR)
})

# ----------------------
# Command line options
# ----------------------
option_list <- list(
  make_option("--sumstats", type="character", help="GWAS summary stats (tabular, with SNP, BETA, SE)"),
  make_option("--ld_matrix", type="character", help="LD matrix file"),
  make_option("--snp_list", type="character", help="SNP list file (same order as LD matrix)"),
  make_option("--L", type="integer", default=-1, help="Number of components (-1 for auto)"),
  make_option("--coverage", type="double", default=0.95, help="Credible set coverage"),
  make_option("--n", type="integer", help="Sample size"),
  make_option("--credible_sets_out", type="character", help="Output file for credible sets"),
  make_option("--pips_out", type="character", help="Output file for SNP PIPs")
)

opt <- parse_args(OptionParser(option_list=option_list))

# ----------------------
# Load data
# ----------------------
sumstats <- read.table(opt$sumstats, header=TRUE, stringsAsFactors=FALSE)
ld <- as.matrix(read.table(opt$ld_matrix, header=FALSE))
snp_list <- read.table(opt$snp_list, header=FALSE, stringsAsFactors=FALSE)[,1]

# ----------------------
# Sanity checks
# ----------------------
if(!all(c("SNP","BETA","SE") %in% colnames(sumstats))){
  stop("Sumstats must contain columns: SNP, BETA, SE")
}

# Ensure SNP order matches LD matrix
sumstats <- sumstats[match(snp_list, sumstats$SNP), ]

if(any(is.na(sumstats$BETA)) || any(is.na(sumstats$SE))){
  stop("Some SNPs in snp_list not found in summary stats.")
}

# ----------------------
# LD matrix fix
# ----------------------
# Force symmetry
ld <- (ld + t(ld)) / 2

# Ensure positive semidefinite (numerical fix)
eig <- eigen(ld, symmetric=TRUE)
eig$values[eig$values < 1e-8] <- 1e-8
ld <- eig$vectors %*% diag(eig$values) %*% t(eig$vectors)

# ----------------------
# Run SuSiE
# ----------------------
if (opt$L == -1) {
  opt$L <- 10  # reasonable default
}

res <- susie_rss(
  bhat = sumstats$BETA,
  shat = sumstats$SE,
  R = ld,
  n = opt$n,
  L = opt$L,
  coverage = opt$coverage,
  max_iter = 1000   # increased from 100
)

# ----------------------
# Save outputs
# ----------------------

# Credible sets
cs_out <- data.frame(
  CS = rep(seq_along(res$sets$cs), lengths(res$sets$cs)),
  SNP = unlist(lapply(res$sets$cs, function(idx) snp_list[idx]))
)
write.table(cs_out, file=opt$credible_sets_out, sep="\t", quote=FALSE, row.names=FALSE)

# PIPs
pips_out <- data.frame(
  SNP = snp_list,
  PIP = res$pip
)
write.table(pips_out, file=opt$pips_out, sep="\t", quote=FALSE, row.names=FALSE)
