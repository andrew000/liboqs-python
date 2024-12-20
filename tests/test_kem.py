import platform  # to learn the OS we're on
import random

import oqs

# KEMs for which unit testing is disabled
disabled_KEM_patterns = []  # noqa: N816

if platform.system() == "Windows":
    disabled_KEM_patterns = ["Classic-McEliece"]  # noqa: N816


def test_correctness() -> tuple[None, str]:
    for alg_name in oqs.get_enabled_kem_mechanisms():
        if any(item in alg_name for item in disabled_KEM_patterns):
            continue
        yield check_correctness, alg_name


def check_correctness(alg_name: str) -> None:
    with oqs.KeyEncapsulation(alg_name) as kem:
        public_key = kem.generate_keypair()
        ciphertext, shared_secret_server = kem.encap_secret(public_key)
        shared_secret_client = kem.decap_secret(ciphertext)
        assert shared_secret_client == shared_secret_server  # noqa: S101


def test_wrong_ciphertext() -> tuple[None, str]:
    for alg_name in oqs.get_enabled_kem_mechanisms():
        if any(item in alg_name for item in disabled_KEM_patterns):
            continue
        yield check_wrong_ciphertext, alg_name


def check_wrong_ciphertext(alg_name: str) -> None:
    with oqs.KeyEncapsulation(alg_name) as kem:
        public_key = kem.generate_keypair()
        ciphertext, shared_secret_server = kem.encap_secret(public_key)
        wrong_ciphertext = bytes(random.getrandbits(8) for _ in range(len(ciphertext)))
        shared_secret_client = kem.decap_secret(wrong_ciphertext)
        assert shared_secret_client != shared_secret_server  # noqa: S101


def test_not_supported() -> None:
    try:
        with oqs.KeyEncapsulation("bogus") as _kem:
            msg = "oqs.MechanismNotSupportedError was not raised."
            raise AssertionError(msg)  # noqa: TRY301
    except oqs.MechanismNotSupportedError:
        pass
    except Exception as ex:  # noqa: BLE001
        msg = f"An unexpected exception was raised. {ex}"
        raise AssertionError(msg)  # noqa: B904


def test_not_enabled() -> None:
    # TODO: test broken as the compiled lib determines which algorithms are supported and enabled
    for alg_name in oqs.get_supported_kem_mechanisms():
        if alg_name not in oqs.get_enabled_kem_mechanisms():
            # Found a non-enabled but supported alg
            try:
                with oqs.KeyEncapsulation(alg_name) as _kem:
                    msg = "oqs.MechanismNotEnabledError was not raised."
                    raise AssertionError(msg)  # noqa: TRY301
            except oqs.MechanismNotEnabledError:
                pass
            except Exception as ex:  # noqa: BLE001
                msg = f"An unexpected exception was raised. {ex}"
                raise AssertionError(msg)  # noqa: B904


if __name__ == "__main__":
    try:
        import nose2

        nose2.main()

    except ImportError:
        import nose

        nose.runmodule()
