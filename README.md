# metamorph
A package for de-identifying data and transforming it for privacy.

# Installation of Alpha
Use `pip install git+https://github.com/samlexrod/metamorph.git` to install the package and its dependencies.

# Features
This package offers a variety of powerful features designed to handle and process data with ease and efficiency, including:

**PII Scrubbing with Scrubadub**: Automatically detects and replaces personally identifiable information in text data to ensure privacy and compliance with data protection regulations.

**Data Mocking with Faker**: Generates fake data for testing and example purposes, ensuring user data remains secure and private.

**Secure Key Masking with UUID4**: Utilizes UUID4 to mask sensitive keys, significantly enhancing data security by ensuring real keys remain undisclosed.

**Flexible Date Manipulation**:

- Random Date Generation: Creates random dates within specified windows, allowing for dynamic data sets that reflect varied timeframes.
- Date Shifting: Provides the ability to push dates forward or backward, enabling simulations of time-sensitive data scenarios or adjustments to temporal data for analysis and testing.
  
These features make metamorph a versatile tool for developers and data scientists working on projects that require high levels of data integrity, security, and variability.


# Dependencies and Security Features
Scrubadub, Faker, and UUID4 are integral to the package’s functionality, offering PII scrubbing, fake data generation, and key masking capabilities. These dependencies ensure that the package operates effectively, with a strong emphasis on privacy and security.

# Usage

```python
from metamorph import Metamorph

morph = Metamorph()

# The following will generate fake names
your_df['fake_sensitive_name'] = morph.transform(series=your_df['sensitive_name'] , type="full name")

# The following will generate fake names
your_df['fake_sensitive_birth_date'] = morph.transform(series=your_df['sensitive_birth_date'] , type="random date")

# The following will generate fake names
your_df['fake_sensitive_date'] = morph.transform(
  series=your_df['sensitive_date'] ,
  type="push date",
  push_method="all",
  push_window=3,
  push_direction="forwards"
)

```


# Contributing
We welcome contributions of all kinds from the community! Whether it's a bug fix, a new feature, or an improvement to our documentation, we appreciate your help in making metamorph better.

To contribute:

Fork the repository on GitHub.
Clone your fork to your local machine.
Create a new branch for your changes.
Make your changes and commit them with clear, descriptive messages.
Push your changes to your fork on GitHub.
Open a pull request against our main branch for review.
Please read our CONTRIBUTING.md file (if available) for more detailed information about contributing guidelines and code of conduct.

# License
This project is licensed under the MIT License - see the LICENSE file for details. The MIT License is a permissive license that is short and to the point. It lets people do anything they want with your code as long as they provide attribution back to you and don’t hold you liable.
