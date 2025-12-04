processSIRData <- function() {
    in_file = "sir_output.csv"
    out_file = "sir_summary.csv"
    horizon_days = 60

    faasr_get_file(remote_file = in_file, local_file = in_file)

    pred <- read.csv(in_file, stringsAsFactors = FALSE)

    required_cols <- c("time", "S", "I", "R")
    missing_cols <- setdiff(required_cols, colnames(pred))
    if (length(missing_cols) > 0) {
        stop("Missing columns in predicted file: ", paste(missing_cols, collapse = ", "))
    }

    # Reconstruct population size 
    N <- pred$S[1] + pred$I[1] + pred$R[1]

    # Compute peak of predicted infection curve 
    peak_idx_pred <- which.max(pred$I)
    I_peak_pred   <- pred$I[peak_idx_pred]
    t_peak_pred   <- pred$time[peak_idx_pred]

    # Final epidemic size and attack rate
    R_final   <- tail(pred$R, 1)
    attack_rt <- R_final / N


    summary_df <- data.frame(
        N                  = N,
        I_peak_pred        = I_peak_pred,
        t_peak_pred        = t_peak_pred,
        peak_prevalence    = I_peak_pred / N,
        R_final            = R_final,
        attack_rate        = attack_rt
    )

    write.csv(summary_df, out_file, row.names = FALSE)
    faasr_put_file(local_file = out_file, remote_file = out_file)

    return(0)
}

