class Shotkit < Formula
  desc "App Store screenshot pipeline: auto-capture, composite, and validate"
  homepage "https://github.com/nicolocurioni96/withnico-skills"
  url "https://github.com/nicolocurioni96/withnico-skills/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e7fb9c7a5f079075b0329fbc133b8c682145cd8696aacfc8ec77fe69f839a0bc"
  license "MIT"
  version "1.0.0"

  depends_on :macos
  depends_on "python@3"

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
