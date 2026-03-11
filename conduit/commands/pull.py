from conduit.providers.hugging_face import HuggingFace


def run(args):
    quant = None
    if not args:
        print("Usage: conduit install <model_repo>")
        return

    repo = args[0]
    try:
        quant = args[1]
    except:
        pass

    try:
        hf = HuggingFace()
        if quant:
            hf.install(repo, quant)
        else:
            hf.install(repo)
            
    except Exception as e:
        print("\nInstall Failed")
        print(str(e))
