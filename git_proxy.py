"""在终端交互管理 Git 全局代理，无需安装第三方库。"""

import shutil
import subprocess


PROXY = "http://127.0.0.1:7897"
KEYS = ("http.proxy", "https.proxy")


def git_config(*args):
    """通过参数列表执行 Git，避免 shell 命令拼接。"""
    return subprocess.run(
        ["git", "config", "--global", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def show_status():
    print("\n当前 Git 全局代理：")
    for key in KEYS:
        result = git_config("--get-all", key)
        if result.returncode == 0:
            print(f"  {key}: {result.stdout.strip()}")
        elif result.returncode == 1:
            print(f"  {key}: 未设置")
        else:
            print(f"  读取 {key} 失败：{result.stderr.strip()}")


def change_proxy(enable):
    success = True
    for key in KEYS:
        if enable:
            result = git_config("--replace-all", key, PROXY)
            allowed_codes = (0,)
        else:
            result = git_config("--unset-all", key)
            # Git 在配置项不存在时返回 5，这也意味着无需取消。
            allowed_codes = (0, 5)
        if result.returncode not in allowed_codes:
            success = False
            print(f"修改 {key} 失败：{result.stderr.strip()}")

    if success:
        if enable:
            print(f"\n已开启 Git 全局代理：{PROXY}")
            print("请确保 Clash Verge 已运行，且代理端口为 7897。")
        else:
            print("\n已移除 Git 全局 http.proxy 和 https.proxy 配置。")
    else:
        print("\n部分配置修改失败，请检查下面的当前状态。")
    show_status()


def main():
    if shutil.which("git") is None:
        print("未找到 Git，请先安装 Git 并将其加入 PATH。")
        return 1

    print("Git 代理管理 · Clash Verge · 127.0.0.1:7897")
    print("设置作用于当前用户的 Git 全局配置，开启时会覆盖原有代理值。")
    print("不修改环境变量、仓库局部配置或针对特定 URL 的代理配置。")
    show_status()

    while True:
        print("\n1. 开启代理\n2. 取消代理\n3. 查看状态\n0. 退出")
        try:
            choice = input("请选择 [0/1/2/3]：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            return 0

        if choice == "0":
            print("已退出。")
            return 0
        if choice == "1":
            change_proxy(True)
        elif choice == "2":
            change_proxy(False)
        elif choice == "3":
            show_status()
        else:
            print("输入无效，请输入 0、1、2 或 3。")


if __name__ == "__main__":
    raise SystemExit(main())
