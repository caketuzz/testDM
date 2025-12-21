
import pytest

from app.domain.services.code_generator import generate_activation_code


async def test_generate_activation_code_is_generated_and_four_digits():

    code = generate_activation_code()

    assert(code)
    assert(len(str(code)) == 4)


