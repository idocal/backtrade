from agents.SingleDQNAgent import SingleDQNAgent
from envs.SingleAssetEnv import SingleAssetEnv
from stable_baselines3.common.env_checker import check_env
import json


if __name__ == "__main__":
    config = json.load(open("config.json"))
    # train agent
    train_config = config['train']
    env = SingleAssetEnv(train_config)
    check_env(env)
    agent = SingleDQNAgent(env)
    num_train_steps = train_config["num_steps"]
    agent.learn(num_train_steps)

    # test agent
    test_config = config['test']
    test_env = SingleAssetEnv(test_config)
    check_env(test_env)
    obs = test_env.reset()
    while True:
        action = agent.predict(obs)
        obs, reward, done, info = test_env.step(action)
        if done:
            break
