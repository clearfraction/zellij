Name:           zellij
Version:        %(unset https_proxy && curl -s https://api.github.com/repos/zellij-org/zellij/releases/latest | grep -oP '"tag_name": "v\K(.*)(?=")')
Release:        1
URL:            https://github.com/zellij-org/zellij
Source0:        https://github.com/zellij-org/zellij/archive/refs/tags/v%{version}.tar.gz
Summary:        A terminal multiplexer
License:        MIT
BuildRequires:  rustc
BuildRequires:  pkg-config
BuildRequires:  libxcb-dev
BuildRequires:  freetype-dev
BuildRequires:  xclip
BuildRequires:  fontconfig-dev
BuildRequires:  mesa-dev
BuildRequires:  libxkbcommon-dev
BuildRequires:  ncurses-dev
BuildRequires:  curl-dev
 
%description
Alacritty is a terminal emulator written in Rust that leverages the GPU for
rendering.

%prep
%setup -q
# Remove prebuilt binaries
rm -rvf zellij-utils/assets/plugins/*


%build
unset http_proxy https_proxy no_proxy
export RUSTFLAGS="$RUSTFLAGS -C target-cpu=westmere -C target-feature=+avx -C opt-level=3 -C codegen-units=1 -C panic=abort -Clink-arg=-Wl,-z,now,-z,relro,-z,max-page-size=0x4000,-z,separate-code "

# (c) opensuse style: https://build.opensuse.org/projects/utilities/packages/zellij/files/zellij.spec?expand=1
# First rebuilt plugins we just deleted
# Note: RUSTFLAGS break linking with WASM-files, so we don't use the cargo_build-macro here
pushd default-plugins/compact-bar
cargo build --release --target=wasm32-wasi
popd
pushd default-plugins/status-bar
cargo build --release --target=wasm32-wasi
popd
pushd default-plugins/tab-bar
cargo build --release --target=wasm32-wasi
popd
pushd default-plugins/strider
cargo build --release --target=wasm32-wasi
popd
pushd default-plugins/session-manager
cargo build --release --target=wasm32-wasi
popd
pushd default-plugins/fixture-plugin-for-tests
cargo build --release --target=wasm32-wasi
popd
pushd default-plugins/configuration
cargo build --release --target=wasm32-wasi
popd
pushd default-plugins/plugin-manager
cargo build --release --target=wasm32-wasi
popd


# Move the results to the place they are expected
mv -v target/wasm32-wasi/release/*.wasm zellij-utils/assets/plugins/

cargo build --release --features unstable

for shell in "zsh" "bash" "fish"
do
  ./target/release/zellij setup --generate-completion "$shell" > target/zellij."$shell"
done



%install
install -Dm644 -T ./target/zellij.bash %{buildroot}/usr/share/bash-completion/completions/zellij
install -Dm644 -T ./target/zellij.fish %{buildroot}/usr/share/fish/vendor_completions.d/zellij.fish
install -Dm644 -T ./target/zellij.zsh %{buildroot}/usr/share/zsh/site-functions/_zellij
install -Dm644 -T %{_builddir}/%{name}-%{version}/assets/logo.png %{buildroot}%{_datadir}/pixmaps/%{name}.png
install -Dm644 -T %{_builddir}/%{name}-%{version}/assets/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
install -Dm755 target/release/zellij -t %{buildroot}/usr/bin
strip --strip-debug %{buildroot}/usr/bin/zellij

%files
%defattr(-,root,root,-)
%license MIT
/usr/bin/zellij
/usr/share/applications/zellij.desktop
/usr/share/pixmaps/zellij.svg
/usr/share/bash-completion
/usr/share/fish
/usr/share/zsh
