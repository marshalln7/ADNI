# Load necessary libraries
library(randomForest)
library(caret)  # Needed for data partitioning

# Load the iris dataset
data(iris)

# Split the data into training and validation sets
set.seed(42)
trainIndex <- createDataPartition(iris$Species, p = 0.75, list = FALSE)
trainData <- iris[trainIndex, ]
valData <- iris[-trainIndex, ]

# Handle NA values using na.roughfix from the randomForest package
trainData <- na.roughfix(trainData)
valData <- na.roughfix(valData)

# Train a Random Forest model
model <- randomForest(Species ~ ., data = trainData, ntree = 1000, importance = TRUE)

# Perform permutation importance analysis using randomForest's importance function
importance_results <- importance(model)
print(importance_results)

# Predict on the validation set
predictions <- predict(model, valData)

# Calculate prediction accuracy
accuracy <- sum(predictions == valData$Species) / nrow(valData)
print(paste("Prediction Accuracy:", round(accuracy * 100, 2), "%"))
