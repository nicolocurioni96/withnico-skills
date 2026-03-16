class Shotkit < Formula
  desc "App Store screenshot pipeline: auto-capture, composite, and validate"
  homepage "https://github.com/nicolocurioni96/withnico-skills"
  url "https://github.com/nicolocurioni96/withnico-skills/archive/refs/tags/v1.0.0.tar.gz"
  sha256 ""
  license "MIT"
  version "1.0.0"

  depends_on :macos
  depends_on "python@3"

  resource "Pillow" do
    url "https://files.pythonhosted.org/packages/cd/74/ad3d526f3bf7b6d3f408b73fde271ec69dfac8571571f9a90f1e83ee97a5/pillow-11.1.0.tar.gz"
    sha256 "0f7c276c05a9767e877a0b4c5571b3c66ad1d7e2f1f3a0e7e28e9f0a5a0e7b1a"
  end

  def install
    # Install scripts to libexec
    libexec.install Dir["skills/shotkit/scripts/*"]
    libexec.install Dir["skills/shotkit/assets"]
    libexec.install Dir["skills/shotkit/references"]

    # Install Python dependencies into libexec
    venv = libexec/"vendor"
    system "python3", "-m", "venv", venv.to_s
    venv_pip = venv/"bin/pip3"
    system venv_pip.to_s, "install", "Pillow"

    # Create wrapper that sets up PATH to use venv python
    (bin/"shotkit").write <<~EOS
      #!/bin/bash
      export PATH="#{libexec}/vendor/bin:$PATH"
      exec "#{libexec}/shotkit" "$@"
    EOS
  end

  test do
    assert_match "shotkit", shell_output("#{bin}/shotkit --version")
  end
end
