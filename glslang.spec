# (akien) No soname upstream, arbitrarily using 0 for now
# Without proper soname, the devel package would not generate the
# devel() provides that RPM relies on to pull in the proper deps
# in reverse dependencies.
%define major 11
%define libname %mklibname %{name}
%define devname %mklibname %{name} -d

# Cyclic dependencies between HLSL and glslang, we can't build with --no-undefined
# for the time being: https://github.com/KhronosGroup/glslang/issues/1484
%define _disable_ld_no_undefined 1

# (tpg) reduce the debug
%global optflags %{optflags} -g1

Name:		glslang
Version:	15.0.0
Release:	1
Summary:	Khronos reference front-end for GLSL and ESSL, and sample SPIR-V generator
Group:		System/Libraries
License:	BSD and GPLv3+ and ASL 2.0
URL:		https://github.com/KhronosGroup
Source0:	%url/%{name}/archive/%{version}/%{name}-%{version}.tar.gz
# https://github.com/KhronosGroup/glslang/pull/1621
#Patch1:		0001-CMake-Allow-linking-against-system-installed-SPIRV-T.patch
# https://github.com/KhronosGroup/glslang/pull/2419
#Patch2:		0001-CMake-Make-glslang-default-resource-limits-STATIC.patch
#Patch3:		0002-CMake-Use-VERSION-SOVERSION-for-all-shared-libs.patch
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(SPIRV-Tools)

%description
%{name} is the official reference compiler front end for the OpenGL
ES and OpenGL shading languages. It implements a strict
interpretation of the specifications for these languages.

%package -n %{libname}
Summary:	Library files for %{name}
Group:		System/Libraries
%rename %mklibname glslang 11

%description -n %{libname}
Library files for %{name}.

%package -n %{devname}
Summary:	Development files for %{name}
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
%{name} is the official reference compiler front end for the OpenGL
ES and OpenGL shading languages. It implements a strict
interpretation of the specifications for these languages.

%prep
%autosetup -p1

# Fix rpmlint warning on debuginfo
find . -name '*.h' -or -name '*.cpp' -or -name '*.hpp'| xargs chmod a-x

%build
%cmake \
  -DGLSLANG_SOVERSION=%{major} \
  -DGLSLANG_VERSION=%{version} \
  -G Ninja

%ninja_build

%install
%ninja_install -C build

# For compatibility with old versions
ln -s %{name}/SPIRV %{buildroot}%{_includedir}/

# Not needed, linked into the shared libs
rm -f %{buildroot}%{_libdir}/*.a

%check
cd Test
LD_LIBRARY_PATH+=%{buildroot}%{_libdir} ./runtests localResults %{buildroot}%{_bindir}/glslangValidator %{buildroot}%{_bindir}/spirv-remap
cd -

%files
%doc README.md README-spirv-remap.txt
%{_bindir}/glslangValidator
%{_bindir}/spirv-remap

%files -n %{libname}
%{_libdir}/lib%{name}*.so.%{major}*
%{_libdir}/libHLSL.so.%{major}*
%{_libdir}/libSPIRV.so.%{major}*
%{_libdir}/libSPVRemapper.so.%{major}*

%files -n %{devname}
%{_includedir}/SPIRV
%{_includedir}/%{name}/
%{_libdir}/lib%{name}*.so
%{_libdir}/libHLSL.so
%{_libdir}/libSPIRV.so
%{_libdir}/libSPVRemapper.so
%{_libdir}/cmake/glslang
%{_libdir}/cmake/*.cmake
