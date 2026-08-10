# Data dictionary

Each `batchN.dat` file is a chronological acquisition batch. The first token is the gas class label; the remaining LIBSVM-style `index:value` tokens represent 128 numeric features (eight features for each of 16 sensors). `batch` is ordered 1 through 10. Exact counts and labels are generated in the dataset validation artifacts.
