from data_processor import load_dataset, recommend_exercises

df = load_dataset("howto/utils/gym_exercises.csv")
recommendations = recommend_exercises(df, "Chest")

print(recommendations.head())